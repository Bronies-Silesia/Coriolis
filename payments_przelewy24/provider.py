import json
import logging
from os import getenv
from decimal import Decimal

import requests
from datetime import datetime
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseForbidden
from django.http.response import HttpResponseBadRequest, HttpResponseServerError
from payments import PaymentStatus
from payments.core import BasicProvider
from payments.forms import PaymentForm
from payments.models import BasePayment

from events.models import Event, Ticket, Payment

from payments_przelewy24.api import Transaction
from payments_przelewy24.forms import ProcessForm

from .api import Przelewy24API, Przelewy24Config

CENTS = Decimal("0.01")

logger = logging.getLogger(__name__)


def _create_transaction_from_payment(payment: BasePayment):
    return Transaction(
        sessionId=str(payment.pk),
        amount=int(payment.total / CENTS),
        currency=payment.currency,
        description=payment.description,
        email=payment.billing_email,
        country=payment.billing_country_code,
        language="pl",  # TODO,
    )


class Przelewy24Provider(BasicProvider):
    """Payment provider for Przelewy24.pl
    This backend implements payments using a popular Polish gateway, `Przelewy24.pl
    <http://www.Przelewy24.pl>`_.
    """

    _method = "post"

    def __init__(self, config: Przelewy24Config, **kwargs):
        self._api = Przelewy24API(config)
        self._config = config
        super().__init__(**kwargs)
        if not self._capture:
            raise ImproperlyConfigured("Przelewy24 does not support pre-authorization.")

    def get_action(self, payment):
        url = self._api.register(
            transaction=_create_transaction_from_payment(payment),
            success_url=payment.get_success_url(),
            status_url=self.get_return_url(payment),
        )
        logger.debug(f"Transaction registered: url={url}")
        return url

    def get_form(self, payment, data=None):
        form = super().get_form(payment, data)
        form.action = self.get_action(payment)
        form.method = self._method
        return form

    def get_hidden_fields(self, payment):
        return {}

    def get_payment_response(self, payment, extra_data=None):
        post = self.get_product_data(payment, extra_data)
        return requests.post(self.endpoint, data=post)

    def process_data(self, payment, request):
        logging.info("Process Przelewy24's notification: body={request.body}")
        try:
            data = json.loads(request.body.decode("utf-8"))
            form = ProcessForm(payment=payment, config=self._config, data=data)
            if form.is_valid():
                orderId = data["orderId"]
                self._api.verify(
                    transaction=_create_transaction_from_payment(payment),
                    orderId=orderId,
                )
                form.save()
                payment.change_status(PaymentStatus.CONFIRMED)

                # Wysłanie bileta do API
                try:
                    ticket: Ticket = Ticket.objects.prefetch_related('user', 'event', 'type').get(id=payment.ticket.id)
                except Ticket.DoesNotExist:
                    logging.error(f"Issued a render job for missing ticket: {orderId}")
                    raise Exception("Model not found")

                try:
                    url = getenv('TICKETER_URL')
                    if url == "":
                        raise Exception("bad ticketer url")

                    payload={
                        'ext_order_id': ticket.id,
                        'ext_product_id': ticket.type.name,
                        'name': ticket.name,
                        'email': ticket.email,
                        'client_id': '1',
                        'quantity': '1',
                        'purchase_date': datetime.today().strftime('%Y-%m-%d')
                    }
                    files=[]
                    headers = {}
                    response = requests.request("POST", url, headers=headers, data=payload, files=files)
                    if response.status_code != 200:
                        raise Exception("Renderer returned error !200.")
                    data = response.json()
                    if data.get('success') != "true":
                        raise Exception("Response from renderer returned error.", data.get('message'))
                    return HttpResponse("OK")
                except Exception as e:
                    logger.error(f"{str(e)}, {request.body.decode('utf-8')}")
                    return HttpResponseServerError(e)        

            else:
                error_str = ", ".join([f"{k}: {v}" for k, v in form.errors.items()])
                logger.error(error_str)
                return HttpResponseBadRequest("Failed - incorrect data")
        except Exception as e:
            logger.error(f"{str(e)}, {request.body.decode('utf-8')}")
            return HttpResponseBadRequest("Failed")
        return HttpResponse("OK")

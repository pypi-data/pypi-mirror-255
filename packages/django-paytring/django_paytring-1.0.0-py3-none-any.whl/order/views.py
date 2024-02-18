from typing import Any
from paytring.client import Order, Subscription
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import math
import random


def generate_receipt_id():
    digits = "1234567891"
    receipt_id = ""

    for i in range(6):
        receipt_id += digits[math.floor(random.random() * 10)]
    return receipt_id


def generate_plan_id():
    plan_id = "PLAN"
    digits = "1234567891"
    plan_id = ""

    for i in range(6):
        plan_id += digits[math.floor(random.random() * 10)]

    return plan_id


def get_string_amount(amount):
    amount = str(int(float(amount) * 100))
    return amount


class OrderCreation(APIView):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.order = Order()

    def get_data(self, data, key):
        
        try:
            if data[key] is not None:
                return data[key]
            return None
        except Exception:
            return None

    def post(self, request):

        try:
            requestData = request.data

            receipt_id = generate_receipt_id()

            payment_info = self.get_data(requestData, "payment_info")

            if payment_info is None:
                return Response(data={"message": "Please provide adequet payment info", "status": False})

            callback_url = settings.CALLBACK_URL

            customer_info = self.get_data(requestData, "customer_info")
            
            if customer_info is None:
                return Response(data={"message": "Please provide adequet Customer info", "status": False})

            create_order_response = self.order.create(
                receipt_id=receipt_id,
                payment_info=payment_info,
                callback_url=callback_url,
                customer_info=customer_info
            )

            if create_order_response['response']['status']:

                return Response(data={"message": create_order_response['response'], "status": True})

            return Response(data={"message": create_order_response['response'], "status": False})

        except Exception as e:

            return Response(data={"message": str(e), "status": False})

    def get(self, request, order_id):
        try:

            fetch_order_response = self.order.fetch(order_id)

            if fetch_order_response['response']['status']:

                data = {
                    "receipt_id": fetch_order_response['response']['order']["receipt_id"],
                    "order_id": fetch_order_response['response']['order']['order_id'],
                    "order_status": fetch_order_response['response']['order']['order_status'],
                    "type": fetch_order_response['response']['order']['method'],
                    "amount": fetch_order_response['response']['order']['amount'] / 100,
                    "pg": fetch_order_response['response']['order']["pg"]
                }

                return Response(data={"data": data, "status": True})
            else:
                return Response(data={"message": fetch_order_response['response']['exception']['message'], "status": False})

        except Exception as e:
            return Response(data={"message": str(e), "status": False})
        


    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.order = Order()

    def get_data(self, data, key):
        
        try:
            if data[key] is not None:
                return data[key]
            return None
        except Exception:
            return None

    def post(self, request):

        try:
            requestData = request.data

            receipt_id = generate_receipt_id()

            payment_info = self.get_data(requestData, "payment_info")

            if payment_info is None:
                return Response(data={"message": "Please provide adequet payment info", "status": False})

            callback_url = settings.CALLBACK_URL

            customer_info = self.get_data(requestData, "customer_info")
            
            if payment_info is None:
                return Response(data={"message": "Please provide adequet Customer info", "status": False})

            create_order_response = self.order.create(
                receipt_id=receipt_id,
                payment_info=payment_info,
                callback_url=callback_url,
                customer_info=customer_info
            )

            if create_order_response['response']['status']:

                return Response(data={"message": create_order_response['response'], "status": True})

            return Response(data={"message": create_order_response['response'], "status": False})

        except Exception as e:

            return Response(data={"message": str(e), "status": False})

    def get(self, request, order_id):
        try:

            fetch_order_response = self.order.fetch(order_id)

            if fetch_order_response['response']['status']:

                data = {
                    "receipt_id": fetch_order_response['response']['order']["receipt_id"],
                    "order_id": fetch_order_response['response']['order']['order_id'],
                    "order_status": fetch_order_response['response']['order']['order_status'],
                    "type": fetch_order_response['response']['order']['method'],
                    "amount": fetch_order_response['response']['order']['amount'] / 100,
                    "pg": fetch_order_response['response']['order']["pg"]
                }

                return Response(data={"data": data, "status": True})
            else:
                return Response(data={"message": fetch_order_response['response']['exception']['message'], "status": False})

        except Exception as e:
            return Response(data={"message": str(e), "status": False})
    

class PaytringSubscription(APIView):

    def __init__(self, **kwargs: Any) -> None:

        super().__init__(**kwargs)
        self.subscription = Subscription()

    def get_data(self, data, key):

        try:
            if data[key] is not None:
                return data[key]
            return None
        except Exception:
            return None

    def post(self, request):

        try:
            requestData = request.data

            receipt_id = generate_receipt_id()

            plan_id = self.get_data(requestData, "plan_id")

            callback_url = settings.CALLBACK_URL

            customer_info = self.get_data(requestData, "customer_info")

            billing_info = self.get_data(requestData, "billing_info")

            shipping_info = self.get_data(requestData, "shipping_info")

            subscription_params = {
                "receipt_id": receipt_id,
                "plan_id": plan_id,
                "callback_url": callback_url,
                "customer_info": customer_info,
                "billing_info": billing_info,
                "shipping_info": shipping_info,
            }

            notes = self.get_data(requestData, "notes")

            pg = self.get_data(requestData, "pg")

            pg_pool_id = self.get_data(requestData, "pg_pool_id")

            if notes or pg or pg_pool_id:

                if notes:
                    subscription_params["notes"] = notes
                if pg:
                    subscription_params["pg"] = pg
                if pg_pool_id:
                    subscription_params["pg_pool_id"] = pg_pool_id

                subscription_response = self.subscription.create_subscription(
                    receipt_id=subscription_params["receipt_id"],
                    plan_id=subscription_params["plan_id"],
                    callback_url=subscription_params["callback_url"],
                    customer_info=subscription_params["customer_info"],
                    billing_info=subscription_params["billing_info"],
                    shipping_info=subscription_params["shipping_info"],
                    notes=subscription_params.get("notes"),
                    pg=subscription_params.get("pg"),
                    pg_pool_id=subscription_params.get("pg_pool_id"),
                )

            else:
                subscription_response = self.subscription.create_subscription(
                    receipt_id=subscription_params["receipt_id"],
                    plan_id=subscription_params["plan_id"],
                    callback_url=subscription_params["callback_url"],
                    customer_info=subscription_params["customer_info"],
                    billing_info=subscription_params["billing_info"],
                    shipping_info=subscription_params["shipping_info"],
                )

            if subscription_response['response']["status"]:

                return Response(data={"message": "Subscription Created", "url": subscription_response['response']['url'], "subscription_id": subscription_response['response']['subscription_id'], "status": True})
            else:

                return Response(data={"message": "Subscription Creation Error", "Error" : subscription_response['response']['exception']['message'],"status": True})

        except Exception as e:

            return Response(data={"message": str(e), "status": False})

    def get(self, request, subscription_id):

        try:

            fetched_subscription = self.subscription.fetch_subscription(
                subscription_id=subscription_id)

            if fetched_subscription['response']['status']:
                return Response(data={"data": fetched_subscription['response']['subscription'], "status": True})

            return Response(data={"message": fetched_subscription['response']['exception']['message'], "status": False})

        except Exception as e:

            return Response(data={"message": str(e), "status": False})


class PaytringSubscriptionPlan(APIView):

    def __init__(self, **kwargs: Any) -> None:

        super().__init__(**kwargs)
        self.subscription_plan = Subscription()

    def get_data(self, data, key):

        try:
            if data[key] is not None:
                return data[key]
            return None
        except Exception:
            return None

    def post(self, request):

        try:
            requestData = request.data

            plan_id = generate_plan_id()

            payment_info = self.get_data(requestData, "payment_info")

            plan_info = self.get_data(requestData, "plan_info")

            notes = self.get_data(requestData, "notes")

            if notes:
                subscription_response = self.subscription_plan.create_plan(
                    receipt_id=plan_id,
                    payment_info=payment_info,
                    plan_info=plan_info,
                    notes=notes
                )
            else:
                subscription_response = self.subscription_plan.create_plan(
                    plan_id=plan_id,
                    payment_info=payment_info,
                    plan_info=plan_info,
                )

            if subscription_response['response']["status"]:

                return Response(data={"message": "Subscription Plan Created", "plan_id": subscription_response['response']['plan_id'], "status": True})

            else:

                return Response(data={"message": "Subscription Plan Creation Error", "status": True})

        except Exception as e:

            return Response(data={"message": str(e), "status": False})

    def get(self, request, plan_id):


        try:
            fetched_subscription = self.subscription_plan.fetch_plan(
                plan_id=plan_id)

            if fetched_subscription['response']['status']:
                return Response(data={"data": fetched_subscription['response']['plan'], "status": True})

            return Response(data={"message": self.order_status['response']['exception']['message'], "status": False})

        except Exception as e:

            return Response(data={"message": str(e), "status": False})

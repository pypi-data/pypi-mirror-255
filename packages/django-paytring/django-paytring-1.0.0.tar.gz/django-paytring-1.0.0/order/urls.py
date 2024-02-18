from django.urls import path
from order.views import OrderCreation, PaytringSubscriptionPlan, PaytringSubscription

orderCreateRoute = "create-order"
orderCreateAction = OrderCreation.as_view()

orderFetchRoute = "create-order/<str:order_id>" 

subscriptionPlanCreateRoute = "subscription-plan"
subscriptionPlanCreateAction = PaytringSubscriptionPlan.as_view()

subscriptionPlanFetchRoute = "subscription-plan/<str:plan_id>"  

subscriptionCreateRoute = "subscription"
subscriptionCreateAction = PaytringSubscription.as_view()

subscriptionFetchRoute = "subscription/<str:subscription_id>"

urlpatterns = [
    path(orderCreateRoute, orderCreateAction),
    path(orderFetchRoute, orderCreateAction),
    path(subscriptionPlanCreateRoute, subscriptionPlanCreateAction),
    path(subscriptionPlanFetchRoute, subscriptionPlanCreateAction),
    path(subscriptionCreateRoute, subscriptionCreateAction),
    path(subscriptionFetchRoute, subscriptionCreateAction),
]

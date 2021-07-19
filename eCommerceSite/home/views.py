from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Item, Order, OrderItem, Address, Payment, CouponCode, Refund
from .forms import CheckoutForm, CouponForm, RequestFrom

import random
import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class HomeView(ListView):
    model = Item
    # paginate_by = 1
    template_name = "home/home.html"


class ProductDetailView(DetailView):
    model = Item
    template_name = "home/product_detail.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            return render(self.request, 'home/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "you do not havr item in cart")
            return redirect("/")


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
                'couponform': CouponForm(),
                'DISPLAY_COUPON_FORM': True,
            }
            return render(self.request, 'home/checkout.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "plaese make order")
            return redirect("home:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                name = form.cleaned_data.get('name')
                mobile = form.cleaned_data.get('mobile')
                pin_code = form.cleaned_data.get('pin_code')
                address = form.cleaned_data.get('address')
                apartment_address = form.cleaned_data.get('apartment_address')
                state = form.cleaned_data.get('state')
                # country = form.cleaned_data.get('country')
                # same_shipping_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_address = form.cleaned_data.get('save_address')
                payment_option = form.cleaned_data.get('payment_option')

                billing_address = Address(
                    user=self.request.user,
                    name=name,
                    mobile=mobile,
                    pin_code=pin_code,
                    address=address,
                    apartment_address=apartment_address,
                    state=state,
                    address_type='B'
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # TODO: redirect payment method
                if payment_option == 'S':
                    return redirect('home:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('home:payment', payment_option='paypal')
                else:
                    messages.error(self.request, "Invalid payment option")
                    return redirect('home:checkout'),
        except ObjectDoesNotExist:
            messages.error(self.request, "you do not have item in cart")
            return redirect("/")
        messages.warning(self.request, 'Failed')
        return redirect('home:checkout')


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
            }
            return render(self.request, 'home/payment.html', context)
        else:
            messages.warning(self.request, 'fill billing address')
            return redirect('home:checkout')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total_amount())

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
                description="My First Test Charge (created for API docs)",
            )

            # create payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total_amount()
            payment.save()

            # assign payment to order
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "ordered successfully")
            return redirect("/")

        except stripe.error.CardError as e:
            messages.error(self.request, f"{e.error.message}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            messages.error(self.request, "rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            messages.error(self.request, "invalind")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            messages.error(self.request, "authenticattion error")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            messages.error(self.request, "api connetion error")
            return redirect("/")

        except stripe.error.StripeError as e:
            messages.error(self.request, "server error")
            return redirect("/")

        except Exception as e:
            messages.error(self.request, "send email")
            return redirect("/")


@login_required(login_url='/accounts/login/')
def add_to_cart(request, slug):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                messages.success(request, "Item quantity added to cart")
                return redirect("home:order_summary")
            else:
                messages.success(request, "Added item to cart")
                order.items.add(order_item)
                return redirect("home:order_summary")
        else:
            order_date = timezone.now()
            order = Order.objects.create(
                user=request.user, order_date=order_date)
            order.items.add(order_item)
            messages.success(request, "Added item to cart")
            return redirect("home:order_summary")


@login_required(login_url='/accounts/login/')
def remove_from_cart(request, slug):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                order.items.remove(order_item)
                order_item.quantity = 1
                order_item.save()
                messages.success(request, "Removed item from cart")
                return redirect("home:order_summary")
            else:
                messages.info(request, "This item does not in your cart")
                return redirect("home:product_detail", slug=slug)
        else:
            messages.info(request, "You do not have a active order")
            return redirect("home:product_detail", slug=slug)


@login_required(login_url='/accounts/login/')
def remove_single_item_from_cart(request, slug):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                else:
                    order.items.remove(order_item)
                    order_item.quantity = 1
                order_item.save()
                messages.success(request, "This item quantity wass updated")
                return redirect("home:order_summary")
            else:
                messages.info(request, "This item does not in your cart")
                return redirect("home:order_summary")
        else:
            messages.info(request, "You do not have a active order")
            return redirect("home:order_summary")


def get_coupon(request, code):
    try:
        coupon = CouponCode.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.warning(request, "This code does not valid")
        return redirect("home:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Coupon added successfully")
                return redirect("home:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have a active order")
                return redirect("home:checkout")

    def get(self, *args, **kwargs):
        form = CouponForm()
        return redirect("home:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RequestFrom()
        context = {
            'form': form
        }
        return render(self.request, 'home/refund_from.html', context)

    def post(self, *args, **kwargs):
        form = RequestFrom(self.request.POST or None)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.accepted = True
                refund.email = email
                refund.save()
                messages.info(self.request, "Your request was recieved")
                return redirect("home:request_refund")
            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect("home:request_refund")

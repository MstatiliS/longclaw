import mock
from django.test.client import RequestFactory
from django.test import TestCase
from django.urls import reverse_lazy

from django.core.management import call_command
from six import StringIO

from longclaw.tests.utils import LongclawTestCase, BasketItemFactory, ProductVariantFactory, catch_signal
from longclaw.basket.utils import basket_id
from longclaw.basket.templatetags import basket_tags
from longclaw.basket.context_processors import stripe_key
from longclaw.basket.models import BasketItem

from .signals import basket_modified


class CommandTests(TestCase):
    """Test management commands
    """
    def test_remove_baskets(self):
        """Removing stale baskets.
        Expect that nothiing is removed and the command exits cleanly
        """
        out = StringIO()
        call_command('remove_stale_baskets', '1', stdout=out)
        self.assertIn('Deleted 0 basket items', out.getvalue())


class BasketTest(LongclawTestCase):
    """Round trip API tests
    """
    def setUp(self):
        """Create a basket with things in it
        """
        request = RequestFactory().get('/')
        request.session = {}
        bid = basket_id(request)
        self.item = BasketItemFactory(basket_id=bid)
        BasketItemFactory(basket_id=bid)

    def test_get_basket(self):
        self.get_test('longclaw_basket_list')

    def test_basket_total_items(self):
        response = self.get_test('longclaw_basket_total_items')

    def test_item_quantity(self):
        self.get_test('longclaw_basket_item_count', {'variant_id': self.item.variant.id})

    def test_create_basket_item(self):
        """
        Test creating a new basket item
        """
        variant = ProductVariantFactory()
        self.post_test({'variant_id': variant.id}, 'longclaw_basket_list')

    def test_increase_basket_item(self):
        """
        Test increasing quantity of basket item
        """
        self.post_test({'variant_id': self.item.variant.id}, 'longclaw_basket_list')

    def test_remove_item(self):
        """
        Test removing an item from the basket
        """
        self.del_test('longclaw_basket_detail', {'variant_id': self.item.variant.id})

    def test_missing_data(self):
        """
        Test we get a message and 400 status if we dont send data
        """
        response = self.client.post(reverse_lazy('longclaw_basket_list'))
        self.assertEqual(response.status_code, 400)


    def test_add_to_cart_btn(self):
        """Test the add to cart tag responds
        """
        result = basket_tags.add_to_basket_btn(1)
        self.assertIsNotNone(result)

    def test_ctx_proc(self):
        self.assertIn('STRIPE_KEY', stripe_key(None))


class BasketModifiedSignalTest(LongclawTestCase):
    """Round trip API tests
    """
    def setUp(self):
        """Create a basket with things in it
        """
        request = RequestFactory().get('/')
        request.session = {}
        bid = basket_id(request)
        self.item = BasketItemFactory(basket_id=bid)
        BasketItemFactory(basket_id=bid)

    def test_create_basket_item(self):
        """
        Test creating a new basket item
        """
        with catch_signal(basket_modified) as handler:
            variant = ProductVariantFactory()
            self.post_test({'variant_id': variant.id}, 'longclaw_basket_list')

        handler.assert_called_once_with(
            basket_id=mock.ANY, # TODO: CHECK CORRECT BASKET ID IS SENT
            sender=BasketItem,
            signal=basket_modified,
        )

    def test_increase_basket_item(self):
        """
        Test increasing quantity of basket item
        """
        with catch_signal(basket_modified) as handler:
            self.post_test({'variant_id': self.item.variant.id}, 'longclaw_basket_list')

        handler.assert_called_once_with(
            basket_id=mock.ANY, # TODO: CHECK CORRECT BASKET ID IS SENT
            sender=BasketItem,
            signal=basket_modified,
        )

    def test_remove_item(self):
        """
        Test removing an item from the basket
        """
        with catch_signal(basket_modified) as handler:
            self.del_test('longclaw_basket_detail', {'variant_id': self.item.variant.id})

        handler.assert_called_once_with(
            basket_id=mock.ANY, # TODO: CHECK CORRECT BASKET ID IS SENT
            sender=BasketItem,
            signal=basket_modified,
        )


class BasketModelTest(TestCase):

    def setUp(self):
        self.item = BasketItemFactory()

    def test_increase_quantity(self):
        self.item.increase_quantity()
        self.assertEqual(self.item.quantity, 2)

        self.item.increase_quantity(quantity=10)
        self.assertEqual(self.item.quantity, 12)

    def test_decrease_quantity(self):
        self.item.quantity = 5
        self.item.save()
        self.item.decrease_quantity()
        self.assertEqual(self.item.quantity, 4)

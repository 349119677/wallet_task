from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from .models import *


class TestWalletView(APITestCase):

    def setUp(self):
        self.url = reverse('wallet')
        self.dummyuser = User.objects.create(username="testuser")
        self.wallet = Wallet.objects.create(owned_by=self.dummyuser)
        self.token, _ = Token.objects.get_or_create(user=self.dummyuser)
        self.headers = {
            'HTTP_AUTHORIZATION': 'Token ' +
            self.token.key
        }

    def test_wallet_view_when_disabled(self):
        expected_response = {
            "status": "fail",
            "data": {
                "error": "Wallet is disabled"
            }
        }

        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, expected_response)

    def test_wallet_view_when_enabled(self):
        self.wallet.status = "enabled"
        self.wallet.save()
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")

    def test_enabling_wallet_when_enabled(self):
        self.wallet.status = "enabled"
        self.wallet.save()
        response = self.client.post(self.url, **self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["status"], "fail")

    def test_enabling_wallet_when_disabled(self):
        response = self.client.post(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")

    def test_disabling_wallet_when_disabled(self):
        response = self.client.patch(self.url, **self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["status"], "fail")

    def test_disabling_wallet_when_enabled(self):
        self.wallet.status = "enabled"
        self.wallet.save()
        response = self.client.patch(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")


class TestDepositWithdrawViews(APITestCase):

    def setUp(self):
        self.deposit_url = reverse('deposit')
        self.withdraw_url = reverse('withdraw')
        self.dummyuser = User.objects.create(username="testuser")
        self.wallet = Wallet.objects.create(
            owned_by=self.dummyuser, status="enabled")
        self.token, _ = Token.objects.get_or_create(user=self.dummyuser)
        self.headers = {
            'HTTP_AUTHORIZATION': 'Token ' +
            self.token.key
        }
        self.request_data = {
            "amount": 10000,
            "reference_id": "randomdadsdjnmkn48849-dasda2"
        }

    def test_successful_deposit(self):
        response = self.client.post(
            self.deposit_url, **self.headers, data=self.request_data)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["data"]["deposit"]["amount"], self.request_data["amount"])

    def test_successful_withdrawl(self):
        self.wallet.balance = 20000
        self.wallet.save()
        response = self.client.post(
            self.withdraw_url, **self.headers, data=self.request_data)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["data"]["withdraw"]["amount"], self.request_data["amount"])

    def test_fail_reference_id_not_unique(self):
        Transaction.objects.create(
            reference_id=self.request_data["reference_id"], wallet=self.wallet, transaction_by=self.dummyuser)
        deposit_response = self.client.post(
            self.deposit_url, **self.headers, data=self.request_data)
        self.assertEqual(deposit_response.status_code, 401)
        self.assertEqual(deposit_response.data["status"], "fail")
        withdraw_response = self.client.post(
            self.withdraw_url, **self.headers, data=self.request_data)
        self.assertEqual(withdraw_response.data["status"], "fail")
        self.assertEqual(withdraw_response.status_code, 401)


class TestInitializeAccountView(APITestCase):

    def setUp(self):
        self.url = reverse('init')
        self.dummyuser = User.objects.create(username="testuser")
        self.request_data = {
            "customer_xid": self.dummyuser.id
        }

    def test_init_success(self):
        response = self.client.post(
            self.url, data=self.request_data)
        self.assertEqual(response.data["status"], "success")
        token = Token.objects.get(user=self.dummyuser)
        self.assertEqual(response.data["data"]["token"], token.key)
        self.assertEqual(response.status_code, 201)

    def test_init_fail(self):
        response = self.client.post(
            self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["status"], "fail")

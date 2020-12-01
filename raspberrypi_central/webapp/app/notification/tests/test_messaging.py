from unittest.mock import Mock

from django.test import TestCase

from account.factories import AccountFactory
from notification.factories import UserSettingFactory, UserFreeCarrierFactory, UserTelegramBotChatIdFactory
from notification.out.messaging import Messaging


class MessagingTestCase(TestCase):

    def setUp(self) -> None:
        pass

    def test_send_message(self):
        account = AccountFactory()
        free_carrier = UserFreeCarrierFactory(user=account)
        telegram = UserTelegramBotChatIdFactory(user=account)

        account_setting = UserSettingFactory(user=account, free_carrier=free_carrier, telegram_chat=telegram)

        free_carrier_mock = Mock()
        telegram_mock = Mock()

        messaging = Messaging(telegram_mock, free_carrier_mock)
        msg = '3.14 - hello world'
        messaging.send_message(msg)

        free_carrier_mock.send_message.assert_called_once_with(free_carrier, msg, None)
        telegram_mock.send_message.assert_called_once_with(telegram, msg, None)

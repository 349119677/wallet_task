from rest_framework import serializers
from .utils import encrypt
from .models import *


class InitAccountSerializer(serializers.Serializer):
    customer_xid = serializers.IntegerField(required=True)


class TransactionSerializer(serializers.Serializer):
    reference_id = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)


class TransactionModelSerializer(serializers.ModelSerializer):
    deposited_by = serializers.SerializerMethodField('get_trans_by')
    deposited_at = serializers.SerializerMethodField('get_trans_at')
    withdrawn_by = serializers.SerializerMethodField('get_trans_by')
    withdrawn_at = serializers.SerializerMethodField('get_trans_at')

    reference_id = serializers.SerializerMethodField(
        'get_encrypted_reference_id')

    class Meta:
        model = Transaction
        exclude = ('transactioned_at', 'transaction_by',
                   'wallet', 'transaction_type', )

    def to_representation(self, obj):
        result = super(TransactionModelSerializer, self).to_representation(obj)
        if obj.transaction_type == "withdraw":
            result.pop('deposited_by')
            result.pop('deposited_at')
        else:
            result.pop('withdrawn_by')
            result.pop('withdrawn_at')
        return result

    def get_trans_at(self, obj):
        return str(obj.transactioned_at)

    def get_trans_by(self, obj):
        return str(obj.transaction_by)

    def get_encrypted_reference_id(self, obj):
        return encrypt(obj.reference_id)


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = '__all__'

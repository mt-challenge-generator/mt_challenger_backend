from rest_framework import serializers
from evaluator.models import Testset, Rule, TestItem, Phenomenon


class TestSetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Testset
        fields = "__all__"


class TestItemSerializer(serializers.HyperlinkedModelSerializer):
    rule = serializers.SerializerMethodField("get_linked_rule")

    def get_linked_rule(self, item):
        rule = Rule.objects.filter(pk=item.id)
        if len(rule) == 0:
            return None
        else:
            serialized_rule = RuleSerializer(rule[0], context=self.context)
            return serialized_rule.data

    class Meta:
        model = TestItem
        fields = "__all__"


class PhenomenonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Phenomenon
        # TODO: serialize the category of the phenomenon
        fields = ["name"]


class RuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rule
        fields = "__all__"


# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, max_length=100)
#     confirm_password = serializers.CharField(write_only=True, max_length=100)

#     class Meta:
#         model = User
#         fields = [
#             "id",
#             "username",
#             "password",
#             "confirm_password",
#             "email",
#             "affiliation",
#             "occupation",
#             "reason",
#         ]

#     def create(self, validated_data):
#         password = validated_data.pop("password")
#         confirm_password = validated_data.pop("confirm_password")

#         if password != confirm_password:
#             raise serializers.ValidationError("Passwords do not match.")

#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()
#         return user


# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=150)
#     password = serializers.CharField(max_length=128, write_only=True)

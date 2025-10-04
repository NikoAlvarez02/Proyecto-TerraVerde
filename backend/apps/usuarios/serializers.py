from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    # Campo sólo escritura para crear/actualizar password
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        # Ajustá la lista si tu User tiene otros campos
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "date_joined",
            "password",      # write-only
            "full_name",     # read-only
        ]
        read_only_fields = ["last_login", "date_joined"]

    def get_full_name(self, obj):
        name = f"{obj.last_name or ''}, {obj.first_name or ''}".strip(", ")
        return name or obj.username

    def create(self, validated_data):
        # manejar password correctamente
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            # si no envían password, definí una por defecto (dev) o levantá error
            user.set_password(User.objects.make_random_password())
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

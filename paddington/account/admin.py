from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect, render, reverse
from django.utils.html import format_html
from rest_auth.models import TokenModel
from reversion.admin import VersionAdmin

from account.forms import AddCaredByForm
from account.models import (Communication, CommunicationResponse,
                            CommunicationStatus, CommunicationType,
                            Notification, Profile, Transaction, Wallet, Store)
from paddington.admin import TrackingAdminMixin
from service.utils import intdot
from web3 import Web3, HTTPProvider

ATTRIBUTE_LIST = ['phone', 'email', 'address', 'id_card_no', 'sex']

admin.site.unregister(User)
admin.site.unregister(TokenModel)

w3 = Web3(HTTPProvider("HTTP://172.18.0.1:7545"))

class ProfileInlineAdmin(admin.StackedInline):
    fk_name = "user"
    model = Profile
    extra = 0
    max_num = 0
    can_delete = False
    classes = ['grp-collapse grp-open']
    inline_classes = ['grp-collapse grp-open']
    readonly_fields = (
        'ordered_by',
        'referral_count', 'users_referred_by',
        'last_interaction_at', 'last_order_at',
        'modified', 'last_carer_added_at',
    )

    autocomplete_lookup_fields = {
        'fk': ['referred_by', 'cared_by']
    }
    raw_id_fields = ['referred_by', 'cared_by']

    def referral_count(self, obj):
        return obj.user.referrals.count()

    def users_referred_by(self, obj):
        url = "{}?profile__referred_by_id={}".format(
            reverse('admin:auth_user_changelist'),
            obj.user_id,
        )
        if obj.user_id:
            return format_html(
                '<a href="{}" target="_blank">Users who were referred by this user</a>', url,
            )
        return ''

    def ordered_by(self, obj):
        url = "{}?ordered_by_id={}".format(
            reverse('admin:merchandise_order_changelist'),
            obj.user_id,
        )
        if obj.user_id:
            return format_html(
                '<a href="{}" target="_blank">Orders that were ordered by this user</a>', url,
            )
        return ''

    def get_readonly_fields(self, request, obj=None):
        # Referred by
        if not request.user.has_perm('account.can_update_referred_by'):
            self.readonly_fields = tuple(set(self.readonly_fields + ('referred_by',)))
        else:
            self.readonly_fields = tuple(
                field
                for field in self.readonly_fields
                if field != 'referred_by'
            )

        # Cared by
        if not request.user.has_perm('account.can_update_cared_by'):
            self.readonly_fields = tuple(set(self.readonly_fields + ('cared_by',)))
        else:
            self.readonly_fields = tuple(
                field
                for field in self.readonly_fields
                if field != 'cared_by'
            )

        return self.readonly_fields


class WalletInlineAdmin(admin.StackedInline):
    fk_name = "user"
    model = Wallet
    extra = 0
    max_num = 0
    can_delete = False
    classes = ['grp-collapse grp-open']
    inline_classes = ['grp-collapse grp-open']
    readonly_fields = ('balance', 'modified_at')


class CommunicationInlineFormset(forms.BaseInlineFormSet):

    def save_new(self, form, commit=True):
        if commit and hasattr(form, '_context'):
            context = form._context
            user = context['request'].user
            form.instance.created_by = user

        return super().save_new(form, commit)

class StoreInlineAdmin(admin.StackedInline):
    fk_name = "user"
    model = Store
    extra = 0
    max_num = 0
    can_delete = False
    classes = ['grp-collapse grp-open']
    inline_classes = ['grp-collapse grp-open']

class CommunicationInlineAdmin(admin.TabularInline):
    fk_name = "user"
    formset = CommunicationInlineFormset
    model = Communication
    extra = 0
    classes = ['grp-collapse grp-open']
    inline_classes = ['grp-collapse grp-open']
    readonly_fields = ('created_at', 'created_by')

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'cols': 20, 'rows': 4})},
    }


class CaredByFilter(admin.SimpleListFilter):
    title = 'Cared by'
    parameter_name = 'cared_by'

    def lookups(self, request, model_admin):
        return [('0', None)] + [
            (s.id, s.__str__)
            for s in User.objects.filter(is_active=True, is_staff=True)
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            queryset = queryset.filter(
                profile__cared_by__isnull=True
            )
        elif self.value():
            queryset = queryset.filter(
                profile__cared_by_id=self.value()
            )

        return queryset


@admin.register(User)
class MyUserAdmin(VersionAdmin, UserAdmin):
    list_display = [
        "id", "username", "full_name", "phone", "personal_facebook",
        "internal_comment", "referred_by", 'cared_by', "order_count", "last_order_at",
        "last_interaction_at", "date_joined",
    ]
    list_display_links = ["id", "username"]

    search_fields = (
        'username', 'first_name', 'last_name', 'email',
        'profile__email', 'profile__address', 'profile__internal_comment',
        'profile__personal_facebook',
    )

    def full_name(self, obj):
        return obj.last_name + " " + obj.first_name

    def last_interaction_at(self, obj):
        return hasattr(obj, 'profile') and obj.profile.last_interaction_at

    last_interaction_at.admin_order_field = "profile__last_interaction_at"

    def phone(self, obj):
        return hasattr(obj, 'profile') and obj.profile.phone

    def personal_facebook(self, obj):
        return hasattr(obj, 'profile') and obj.profile.personal_facebook

    def internal_comment(self, obj):
        return hasattr(obj, 'profile') and obj.profile.internal_comment

    def referred_by(self, obj):
        return hasattr(obj, 'profile') and obj.profile.referred_by

    def cared_by(self, obj):
        return hasattr(obj, 'profile') and obj.profile.cared_by

    def order_count(self, obj):
        return obj.order_set.count()

    def last_order_at(self, obj):
        return hasattr(obj, 'profile') and obj.profile.last_order_at

    last_order_at.admin_order_field = "profile__last_order_at"

    def has_delete_permission(self, request, obj=None):
        return False

    def lookup_allowed(self, lookup, value):
        if lookup == 'profile__referred_by_id':
            return True
        return super().lookup_allowed(lookup, value)

    def change_balance(self, obj):
        url = "{}?user={}".format(
            reverse('admin:account_transaction_add'),
            obj.id,
        )
        if obj.id:
            return format_html(
                '<a href="{}" target="_blank">Recharge or withdraw money from this user</a>', url,
            )
        return ''

    def transaction_list(self, obj):
        url = "{}?user_id={}".format(
            reverse('admin:account_transaction_changelist'),
            obj.id,
        )
        if obj.id:
            return format_html(
                '<a href="{}" target="_blank">Transactions related to this user</a>', url,
            )
        return ''

    inlines = [CommunicationInlineAdmin, ProfileInlineAdmin, WalletInlineAdmin, StoreInlineAdmin]
    list_filter = [
        'profile__sex', 'profile__online_sales_experience', CaredByFilter,
    ]
    change_list_template = "admin/change_list_filter_sidebar.html"
    actions = ['add_cared_by']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'first_name', 'last_name',
        )}),
        ('Communication', {
            'classes': ('placeholder communication_set-group',),
            'fields': (),
        }),
        ('Profile', {
            'classes': ('placeholder profile-group',),
            'fields': (),
        }),
        ('Wallet', {
            'classes': ('placeholder wallet-group',),
            'fields': (),
        }),
        ('Store', {
            'classes': ('placeholder store-group',),
            'fields': ()
        }),
        ('Transaction', {
            'fields': ('change_balance', 'transaction_list'),
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        # Disable some fields
        disable_fields = ('is_superuser', 'user_permissions', 'groups', 'is_staff')
        readonly_fields = ('last_login', 'date_joined', 'full_name',
                           'change_balance', 'transaction_list')
        print(w3.isConnected())
        self.readonly_fields += readonly_fields
        if not request.user.is_superuser:
            self.readonly_fields += disable_fields
        else:
            self.readonly_fields = tuple(
                field
                for field in self.readonly_fields
                if field not in disable_fields
            )
        return super().get_form(request, obj, **kwargs)

    def save_formset(self, request, form, formset, change):
        context = {'request': request}
        form._context = context
        print("REQUEST: {}".format(request.user))
        for form in formset:
            form._context = context
        super().save_formset(request, form, formset, change)

    def add_cared_by(self, request, queryset):
        # POST
        if request.POST.get('save'):
            add_cared_by_form = AddCaredByForm(request.POST)
            print(request.POST)
            if add_cared_by_form.is_valid():
                add_cared_by_form.save(commit=True)
                messages.info(
                    request,
                    "Added cared_by to {} user(s)".format(queryset.count()),
                )
                return redirect(request.get_full_path())

            errors_list = [add_cared_by_form.errors]
            messages.add_message(
                request,
                messages.ERROR,
                "\n".join(
                    "\n".join(value)
                    for d in errors_list
                    for value in d.values()
                    if d
                )
            )

        # GET
        user_list = ','.join([str(p.id) for p in queryset])
        add_cared_by_form = AddCaredByForm(initial={
            'user_list': user_list,
            '_selected_action': request.POST.getlist(
                admin.ACTION_CHECKBOX_NAME),
        })

        return render(
            request,
            'admin/account/profile/add_cared_by.html',
            {
                'opts': self.model._meta,
                'has_change_permission': True,
                'form': add_cared_by_form,
                'title': 'Add a carer to users',
            }
        )

    add_cared_by.short_description = "Add a carer to these users"


@admin.register(Transaction)
class TransactionAdmin(TrackingAdminMixin):
    model = Transaction
    autocomplete_lookup_fields = {
        'fk': ['user']
    }
    raw_id_fields = ['user']
    list_display = ['__str__', 'user_', 'amount_', 'post_transaction_balance_',
                    'description', 'created_by', 'created_at', 'success', 'note']
    list_filter = ['success']
    readonly_fields = ('wallet', 'created_by', 'created_at', 'success', 'note',
                       'post_transaction_balance')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def user_(self, obj):
        url = "{}".format(
            reverse('admin:auth_user_change', args=(obj.user_id,)),
        )
        if obj.user_id:
            return format_html(
                '<a href="{}" target="_blank">{}</a>', url, obj.user,
            )
        return ''

    def amount_(self, obj):
        color = 'red' if obj.amount < 0 else 'green'
        return format_html('<span style="color: {};"><strong>{}</strong></span>'.format(
            color, intdot(obj.amount)
        ))

    def post_transaction_balance_(self, obj):
        return intdot(obj.post_transaction_balance)


@admin.register(Notification)
class NotificationAdmin(TrackingAdminMixin):
    list_display = [
        '__str__', 'title', 'content', 'recipients_', 'all_users', 'one_signal_count',
        'remaining', 'failed', 'created_by', 'created_at', 'success',
    ]
    readonly_fields = ['remaining', 'failed', 'one_signal_count', 'created_by',
                       'created_at', 'success']
    search_fields = ['recipients__username', 'title', 'content']

    autocomplete_lookup_fields = {
        'm2m': ['recipients']
    }
    raw_id_fields = ['recipients']

    def recipients_(self, obj):
        return ', '.join([
            u.username
            for u in obj.recipients.all()
        ])

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('Content', {'fields': (
            'title', 'content', 'url',
        )}),
        ('Recipients', {
            'fields': ('all_users', 'recipients'),
        }),
        ('Object', {
            'fields': ('type', 'object_id'),
        }),
        ('OneSignal', {
            'fields': ('remaining', 'failed', 'one_signal_count', 'success'),
        }),
        ('System', {
            'fields': ('created_at', 'created_by'),
        }),
    )


@admin.register(CommunicationType)
class CommunicationTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(CommunicationStatus)
class CommunicationStatusAdmin(admin.ModelAdmin):
    pass


@admin.register(CommunicationResponse)
class CommunicationResponseAdmin(admin.ModelAdmin):
    pass


class TransactionCreatedBy(admin.SimpleListFilter):
    title = 'Created by'
    parameter_name = 'created_by'

    def lookups(self, request, model_admin):
        return [
            (s.id, s.__str__)
            for s in User.objects.filter(is_active=True, is_staff=True)
        ]

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(
                created_by=self.value()
            )

        return queryset


@admin.register(Communication)
class Communication(admin.ModelAdmin):
    list_display = readonly_fields = [
        'id', 'created_at', 'created_by', 'user', 'type',
        'status', 'response', 'internal_comment', 'duration',
        'manual_created_at',
    ]

    list_filter = [TransactionCreatedBy]

    def has_delete_permission(self, request, obj=None):
        return False

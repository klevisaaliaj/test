from django.contrib import admin
from .models import Property, Review, ContactMessage, PropertyInquiry,  ChatMessage, PropertyView


class PropertyAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'owner',
        'property_type',
        'listing_type',
        'status',
        'featured',
        'views',
        'city',
        'price',
        'size',
        'year_built',
        'parking',
        'elevator',
        'favorite_count',
        'reviews_count',
        'inquiries_count',
        'average_rating_admin',
        'created_at'
    )

    list_filter = (
        'property_type',
        'listing_type',
        'status',
        'featured',
        'city',
        'parking',
        'elevator',
        'year_built',
        'created_at'
    )

    search_fields = (
        'title',
        'city',
        'description',
        'property_type',
        'listing_type',
        'owner__username'
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'views',
        'favorite_count',
        'favorite_users',
        'reviews_count',
        'inquiries_count',
        'average_rating_admin'
    )

    ordering = (
        '-created_at',
    )

    exclude = (
        'favorites',
    )

    def favorite_count(self, obj):

        return obj.favorites.count()

    favorite_count.short_description = "Favorite Count"

    def favorite_users(self, obj):

        users = obj.favorites.all()

        if users.exists():

            return ", ".join(
                [user.username for user in users]
            )

        return "No favorites yet"

    favorite_users.short_description = "Users Who Favorited"
    
    def reviews_count(self, obj):

        return obj.reviews.count()

    reviews_count.short_description = "Reviews Count"


    def inquiries_count(self, obj):

        return obj.inquiries.count()

    inquiries_count.short_description = "Inquiries Count"


    def average_rating_admin(self, obj):

        return obj.average_rating

    average_rating_admin.short_description = "Average Rating"

    def save_model(self, request, obj, form, change):

        if not obj.owner:
            obj.owner = request.user

        super().save_model(request, obj, form, change)


class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'property',
        'user',
        'rating',
        'created_at'
    )

    list_filter = (
        'rating',
        'created_at',
        'property'
    )

    search_fields = (
        'user__username',
        'comment',
        'property__title'
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )


class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'email',
        'subject',
        'is_answered',
        'created_at'
    )

    list_filter = (
        'is_answered',
        'created_at'
    )

    search_fields = (
        'name',
        'email',
        'subject',
        'message',
        'admin_reply'
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )


class PropertyInquiryAdmin(admin.ModelAdmin):

    list_display = (
        'property',
        'user',
        'name',
        'email',
        'is_answered',
        'created_at'
    )

    list_filter = (
        'is_answered',
        'created_at',
        'property'
    )

    search_fields = (
        'property__title',
        'user__username',
        'name',
        'email',
        'message',
        'admin_reply'
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )

class ChatMessageAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'question',
        'answer',
        'created_at'
    )

    search_fields = (
        'user__username',
        'question',
        'answer'
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',  
    )

class PropertyViewAdmin(admin.ModelAdmin):

    list_display = (
        'property',
        'user',
        'viewed_at'
    )

    list_filter = (
        'property',
        'user',
        'viewed_at'
    )

    search_fields = (
        'property__title',
        'user__username'
    )

    readonly_fields = (
        'property',
        'user',
        'viewed_at'
    )

    ordering = (
        '-viewed_at',
    )


admin.site.register(Property, PropertyAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(PropertyInquiry, PropertyInquiryAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(PropertyView, PropertyViewAdmin)
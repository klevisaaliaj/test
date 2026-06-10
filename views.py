from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from .models import Property, Review, ContactMessage, PropertyInquiry,  ChatMessage, PropertyView
from .forms import PropertyForm, ReviewForm, ContactMessageForm, PropertyInquiryForm,  ChatMessageForm
from django.db.models import Count


def home(request):

    properties = Property.objects.filter(featured=True)[:3]

    property_count = Property.objects.count()

    city_count = Property.objects.values(
        'city'
    ).distinct().count()

    review_count = Review.objects.count()

    chat_form = ChatMessageForm()

    chat_messages = None

    if request.user.is_authenticated and not request.user.is_staff:

        chat_messages = ChatMessage.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        if request.method == 'POST' and 'chatbot_submit' in request.POST:

            chat_form = ChatMessageForm(request.POST)

            if chat_form.is_valid():

                chat_message = chat_form.save(
                    commit=False
                )

                chat_message.user = request.user

                question = chat_message.question.lower()

                available_count = Property.objects.filter(
                    status='Available'
                ).count()

                apartment_count = Property.objects.filter(
                    property_type='Apartment'
                ).count()

                villa_count = Property.objects.filter(
                    property_type='Villa'
                ).count()

                office_count = Property.objects.filter(
                    property_type='Office'
                ).count()

                most_expensive_property = Property.objects.order_by(
                    '-price'
                ).first()

                if 'available' in question:

                    chat_message.answer = (
                        f'We currently have {available_count} available properties listed on our website.'
                    )

                elif 'apartment' in question or 'apartments' in question:

                    chat_message.answer = (
                        f'We currently have {apartment_count} apartments listed. You can filter them from the Properties page.'
                    )

                elif 'villa' in question or 'villas' in question:

                    chat_message.answer = (
                        f'We currently have {villa_count} villas listed. You can view them using the Category filter.'
                    )

                elif 'office' in question or 'offices' in question:

                    chat_message.answer = (
                        f'We currently have {office_count} offices listed. You can view them using the Category filter.'
                    )

                elif 'most expensive' in question or 'highest price' in question:

                    if most_expensive_property:

                        chat_message.answer = (
                            f'The most expensive property is {most_expensive_property.title} with a price of €{most_expensive_property.price}.'
                        )

                    else:

                        chat_message.answer = (
                            'There are no properties listed at the moment.'
                        )

                elif 'price' in question or 'cost' in question:

                    chat_message.answer = (
                        'Property prices are shown on each property details page.'
                    )

                elif 'rent' in question:

                    chat_message.answer = (
                        'You can use the Listing filter to find monthly or daily rental properties.'
                    )

                elif 'buy' in question or 'sale' in question:

                    chat_message.answer = (
                        'You can select For Sale in the Listing filter to view properties available for purchase.'
                    )

                elif 'contact' in question or 'agent' in question:

                    chat_message.answer = (
                        'You can contact our team from the About page or send an inquiry from a property details page.'
                    )

                else:

                    chat_message.answer = (
                        'Thank you for your question. Our team will review it and assist you as soon as possible.'
                    )

                chat_message.save()

                return redirect('home')

    context = {
        'properties': properties,
        'property_count': property_count,
        'city_count': city_count,
        'review_count': review_count,
        'chat_form': chat_form,
        'chat_messages': chat_messages,
    }

    return render(
        request,
        'properties/index.html',
        context
    )

def properties_page(request):

    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()
    listing_type = request.GET.get('listing_type', '').strip()
    status = request.GET.get('status', '').strip()
    sort = request.GET.get('sort', '').strip()

    properties = Property.objects.all()

    if search != '':
        properties = properties.filter(
            Q(title__icontains=search) |
            Q(city__icontains=search) |
            Q(property_type__icontains=search) |
            Q(listing_type__icontains=search)
        )

    if category != '':
        properties = properties.filter(property_type__iexact=category)

    if listing_type != '':
        properties = properties.filter(listing_type__iexact=listing_type)

    if status != '':
        properties = properties.filter(status__iexact=status)

    if sort == 'price_low':
        properties = properties.order_by('price')

    elif sort == 'price_high':
        properties = properties.order_by('-price')

    elif sort == 'newest':
        properties = properties.order_by('-created_at')

    paginator = Paginator(properties, 6)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {
        'properties': page_obj.object_list,
        'page_obj': page_obj,
        'property_count': properties.count(),
        'search': search,
        'category': category,
        'listing_type': listing_type,
        'status': status,
        'sort': sort,
    }

    return render(request, 'properties/properties.html', context)


def details(request, id):

    property = get_object_or_404(Property, id=id)

    property.views += 1
    property.save(update_fields=['views'])

    PropertyView.objects.create(
    property=property,
    user=request.user if request.user.is_authenticated else None
)

    reviews = property.reviews.all()

    form = ReviewForm()

    inquiry_form = PropertyInquiryForm()

    if request.method == 'POST' and 'send_inquiry' in request.POST:

        inquiry_form = PropertyInquiryForm(request.POST)

        if inquiry_form.is_valid():

            inquiry = inquiry_form.save(commit=False)

            inquiry.property = property

            if request.user.is_authenticated:
                inquiry.user = request.user

            inquiry.save()

            messages.success(
                request,
                'Inquiry sent successfully.'
            )

            return redirect('details', id=property.id)

    elif request.method == 'POST':

        if not request.user.is_authenticated:

            messages.error(
                request,
                'You must login to leave a review.'
            )

            return redirect('login')

        existing_review = Review.objects.filter(
            property=property,
            user=request.user
        ).first()

        if existing_review:

            messages.error(
                request,
                'You have already reviewed this property.'
            )

            return redirect('details', id=property.id)

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.property = property

            review.user = request.user

            review.save()

            messages.success(
                request,
                'Review submitted successfully.'
            )

            return redirect('details', id=property.id)

    context = {
        'property': property,
        'reviews': reviews,
        'form': form,
        'inquiry_form': inquiry_form
    }

    return render(
        request,
        'properties/details.html',
        context
    )


@staff_member_required
def create_property(request):

    form = PropertyForm()

    if request.method == 'POST':

        form = PropertyForm(request.POST, request.FILES)

        if form.is_valid():

            property = form.save(commit=False)

            property.owner = request.user

            property.save()

            messages.success(request, 'Property created successfully.')

            return redirect('details', id=property.id)

    context = {
        'form': form,
        'title': 'Create Property'
    }

    return render(request, 'properties/property_form.html', context)


@staff_member_required
def edit_property(request, id):

    property = get_object_or_404(Property, id=id)

    if property.owner != request.user and not request.user.is_staff:

        messages.error(
            request,
            'You do not have permission to edit this property.'
        )

        return redirect('details', id=property.id)

    form = PropertyForm(instance=property)

    if request.method == 'POST':

        form = PropertyForm(request.POST, request.FILES, instance=property)

        if form.is_valid():

            form.save()

            messages.success(request, 'Property updated successfully.')

            return redirect('details', id=property.id)

    context = {
        'form': form,
        'property': property,
        'title': 'Edit Property'
    }

    return render(request, 'properties/property_form.html', context)


@staff_member_required
def delete_property(request, id):

    property = get_object_or_404(Property, id=id)

    if property.owner != request.user and not request.user.is_staff:

        messages.error(
            request,
            'You do not have permission to delete this property.'
        )

        return redirect('details', id=property.id)

    if request.method == 'POST':

        property.delete()

        messages.success(request, 'Property deleted successfully.')

        return redirect('properties')

    context = {
        'property': property
    }

    return render(request, 'properties/property_confirm_delete.html', context)


def about(request):

    form = ContactMessageForm()

    if request.method == 'POST':

        form = ContactMessageForm(request.POST)

        if form.is_valid():

            contact_message = form.save(commit=False)

            if request.user.is_authenticated:
                contact_message.user = request.user

            contact_message.save()

            messages.success(
                request,
                'Message sent successfully.'
            )

            return redirect('about')

    context = {
        'form': form
    }

    return render(
        request,
        'properties/about.html',
        context
    )


def register(request):

    form = UserCreationForm()

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            messages.success(request, 'Account created successfully.')

            return redirect('home')

    context = {
        'form': form
    }

    return render(request, 'properties/register.html', context)


@login_required
def my_messages(request):

    contact_messages = ContactMessage.objects.filter(
        user=request.user
    )

    property_inquiries = PropertyInquiry.objects.filter(
        user=request.user
    )

    context = {
        'contact_messages': contact_messages,
        'property_inquiries': property_inquiries
    }

    return render(
        request,
        'properties/my_messages.html',
        context
    )
@login_required
def toggle_favorite(request, id):

    property = get_object_or_404(Property, id=id)

    if request.user.is_staff:
        messages.error(
            request,
            'Admin accounts cannot add favorites.'
        )

        return redirect('details', id=property.id)

    if property.favorites.filter(id=request.user.id).exists():

        property.favorites.remove(request.user)

        messages.success(
            request,
            'Property removed from favorites.'
        )

    else:

        property.favorites.add(request.user)

        messages.success(
            request,
            'Property added to favorites.'
        )

    return redirect('details', id=property.id)


@login_required
def my_favorites(request):

    properties = request.user.favorite_properties.all()

    context = {
        'properties': properties
    }

    return render(
        request,
        'properties/my_favorites.html',
        context
    )
    
@staff_member_required
def favorites_report(request):

    properties = Property.objects.annotate(
        favorite_count=Count('favorites')
    ).filter(
        favorite_count__gt=0
    ).order_by(
        '-favorite_count'
    )

    context = {
        'properties': properties
    }

    return render(
        request,
        'properties/favorites_report.html',
        context
    )

@staff_member_required
def most_viewed_report(request):

    properties = Property.objects.filter(
        views__gt=0
    ).order_by(
        '-views'
    )

    context = {
        'properties': properties
    }

    return render(
        request,
        'properties/most_viewed_report.html',
        context
    )

@staff_member_required
def admin_dashboard(request):

    total_properties = Property.objects.count()

    total_reviews = Review.objects.count()

    total_inquiries = PropertyInquiry.objects.count()

    total_contact_messages = ContactMessage.objects.count()

    total_favorites = 0

    for property in Property.objects.all():
        total_favorites += property.favorites.count()

    most_viewed_property = Property.objects.order_by(
        '-views'
    ).first()

    most_favorited_property = Property.objects.annotate(
        favorite_count=Count('favorites')
    ).order_by(
        '-favorite_count'
    ).first()

    context = {
        'total_properties': total_properties,
        'total_reviews': total_reviews,
        'total_inquiries': total_inquiries,
        'total_contact_messages': total_contact_messages,
        'total_favorites': total_favorites,
        'most_viewed_property': most_viewed_property,
        'most_favorited_property': most_favorited_property
    }

    return render(
        request,
        'properties/admin_dashboard.html',
        context
    )
 
@staff_member_required
def top_rated_report(request):

    properties = Property.objects.all()

    rated_properties = []

    for property in properties:

        if property.reviews.exists():

            rated_properties.append(property)

    rated_properties = sorted(
        rated_properties,
        key=lambda property: property.average_rating,
        reverse=True
    )

    context = {
        'properties': rated_properties
    }

    return render(
        request,
        'properties/top_rated_report.html',
        context
    )

@login_required
def chatbot(request):

    form = ChatMessageForm()

    chat_messages = ChatMessage.objects.filter(
        user=request.user
    )

    if request.method == 'POST':

        form = ChatMessageForm(request.POST)

        if form.is_valid():

            chat_message = form.save(commit=False)

            chat_message.user = request.user

            question = chat_message.question.lower()

            if 'price' in question or 'cost' in question:
                chat_message.answer = 'Property prices are shown on each property details page.'

            elif 'rent' in question:
                chat_message.answer = 'You can find monthly and daily rental properties in the Properties page by using the Listing filter.'

            elif 'buy' in question or 'sale' in question:
                chat_message.answer = 'Properties for sale can be found by selecting For Sale in the Listing filter.'

            elif 'contact' in question or 'agent' in question:
                chat_message.answer = 'You can contact our team from the About page or send a property inquiry from the details page.'

            elif 'available' in question:
                chat_message.answer = 'Property availability is shown using the status badge: Available, Pending, Rented, or Sold.'

            else:
                chat_message.answer = 'Thank you for your question. Our team will review it and assist you as soon as possible.'

            chat_message.save()

            messages.success(
                request,
                'Chat message sent successfully.'
            )

            return redirect('chatbot')

    context = {
        'form': form,
        'chat_messages': chat_messages
    }

    return render(
        request,
        'properties/chatbot.html',
        context
    )

def logout_user(request):

    logout(request)

    messages.success(request, 'You logged out successfully.')

    return redirect('home')
from io import (
    BytesIO,
)


from django.conf import (
    settings,
)
from django.contrib.sites.models import (
    Site,
)
from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
)
from django.core.mail import (
    EmailMultiAlternatives,
)
from django.core.paginator import (
    EmptyPage,
    PageNotAnInteger,
    Paginator,
)
from django.db import (
    IntegrityError,
)
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import (
    render,
)
from django.template.loader import (
    get_template,
)
from django.urls import (
    reverse,
)
from django.utils import (
    timezone,
)
from django.views.decorators.csrf import (
    csrf_exempt,
)


from PIL import (
    Image,
)


from .forms import (
    GetSubscriberForm,
    ModifySubscriberForm,
)
from .models import (
    EmailTracker,
    SiteProfile,
    Subscriber,
    Subscription,
)


def get_universal_email_directory():
    try:
        return settings.EMAILER_EMAIL_TEMPLATES
    except AttributeError:
        return 'django_simple_bulk_emailer/universal/emails'


def get_universal_page_directory():
    try:
        return settings.EMAILER_PAGE_TEMPLATES
    except AttributeError:
        return 'django_simple_bulk_emailer/universal/pages'


def send_email(email_content, list_slug='', subscriber_key='', subject='', text_template='', html_template='', to_address=''):
    try:
        from_address = settings.EMAILER_FROM_ADDRESS
    except AttributeError:
        from_address = settings.DEFAULT_FROM_EMAIL
    try:
        reply_address = settings.EMAILER_REPLY_ADDRESS
    except AttributeError:
        reply_address = from_address
    site_domain = Site.objects.get_current().domain
    site_profile = SiteProfile.objects.filter(
        domain=site_domain,
    ).first()
    protocol_domain = site_profile.protocol_domain()
    manage_url = reverse(
        'django_simple_bulk_emailer:manage_subscriptions',
        kwargs={
            'subscriber_key': subscriber_key,
        },
    )
    if list_slug != '':
        unsubscribe_url = reverse(
            'django_simple_bulk_emailer:quick_unsubscribe',
            kwargs={
                'list_slug': list_slug,
                'subscriber_key': subscriber_key,
            },
        )
    else:
        unsubscribe_url = ''
    subscriptions_url = f'{protocol_domain}{manage_url}'
    quick_unsubscribe_url = f'{protocol_domain}{unsubscribe_url}'
    email_content['subscriptions_url'] = subscriptions_url
    email_content['quick_unsubscribe_url'] = quick_unsubscribe_url
    text_email = get_template(text_template).render(email_content)
    html_email = get_template(html_template).render(email_content)
    message = EmailMultiAlternatives(
        subject,
        text_email,
        from_address,
        [to_address],
        reply_to=[reply_address],
    )
    message.attach_alternative(html_email, 'text/html')
    try:
        message.send(
            fail_silently=True,
        )
    except IOError:
        pass


def get_subscriptions(request):
    """ """
    ''' Begin getting time elements '''
    form_submit_time = timezone.now().timestamp()
    if 'form_load_time' in request.session:
        form_load_time = request.session['form_load_time']
        del request.session['form_load_time']
    else:
        form_load_time = form_submit_time
    ''' End getting time elements '''
    form = GetSubscriberForm
    if request.method == 'POST':
        form = GetSubscriberForm(request.POST)
        if form.is_valid():
            success_template = f'{get_universal_page_directory()}/subscribe_success.html'
            ''' Begin checking for input in hidden field '''
            email = form.cleaned_data['email']
            if email:
                return render(
                    request,
                    success_template,
                )
            ''' End checking for input in hidden field '''
            ''' Begin checking how quickly form was submitted '''
            if form_submit_time - form_load_time < 1:
                return render(
                    request,
                    success_template,
                )
            ''' End checking how quickly form was submitted '''
            subscriber_email = form.cleaned_data['subscriber_email'].lower()
            email_content = {}
            subscriber, created = Subscriber.objects.get_or_create(
                subscriber_email=subscriber_email,
            )
            text_template = f'{get_universal_email_directory()}/subscribe_email_text.txt'
            html_template = f'{get_universal_email_directory()}/subscribe_email_html.html'
            try:
                subject = settings.EMAILER_SUBSCRIBE_SUBJECT
            except AttributeError:
                subject = 'Manage your email subscriptions'
            send_email(
                email_content,
                subscriber_key=subscriber.subscriber_key,
                text_template=text_template,
                html_template=html_template,
                subject=subject,
                to_address=subscriber_email,
            )
            return render(
                request,
                success_template,
            )
    ''' Begin setting when form was submitted '''
    request.session['form_load_time'] = timezone.now().timestamp()
    ''' End setting when form was submitted '''
    page_template = f'{get_universal_page_directory()}/subscribe.html'
    subscription_set = Subscription.objects.filter(
        publicly_visible=True,
    )
    context = {
        'form': form,
        'subscription_set': subscription_set,
    }
    return render(
        request,
        page_template,
        context,
    )


def manage_subscriptions(request, subscriber_key):
    try:
        subscriber = Subscriber.objects.get(
            subscriber_key=subscriber_key,
        )
        subscription_set = subscriber.subscriptions.all()
        form = ModifySubscriberForm(
            initial={
                'subscription_choices': subscription_set,
            },
            instance=subscriber,
        )
        if request.method == 'POST':
            success_template = f'{get_universal_page_directory()}/manage_subscriptions_success.html'
            if 'unsubscribe_all' in request.POST:
                subscriber.subscriptions.clear()
                return render(
                    request,
                    success_template,
                )
            form = ModifySubscriberForm(
                request.POST,
                instance=subscriber,
            )
            if form.is_valid():
                form.save(commit=False)
                subscriber.subscriptions.set(form.cleaned_data['subscription_choices'])
                subscriber.save()
                return render(
                    request,
                    success_template,
                )
        page_template = f'{get_universal_page_directory()}/manage_subscriptions.html'
        context = {
            'form': form,
            'subscriber': subscriber,
            'subscription_set': subscription_set,
        }
        return render(
            request,
            page_template,
            context,
        )
    except ObjectDoesNotExist:
        subscribe_url = reverse(
            'django_simple_bulk_emailer:get_subscriptions',
        )
        page_template = f'{get_universal_page_directory()}/manage_subscriptions_error.html'
        context = {
            'subscribe_url': subscribe_url,
        }
        return render(
            request,
            page_template,
            context,
        )


def quick_unsubscribe(request, list_slug, subscriber_key):
    try:
        subscriber = Subscriber.objects.get(
            subscriber_key=subscriber_key,
        )
        subscription = subscriber.subscriptions.get(
            list_slug=list_slug,
        )
        subscriber.subscriptions.remove(subscription)
        manage_url = reverse(
            'django_simple_bulk_emailer:manage_subscriptions',
            kwargs={
                'subscriber_key': subscriber.subscriber_key,
            }
        )
        page_template = f'{get_universal_page_directory()}/quick_unsubscribe.html'
        context = {
            'list_name': subscription.list_name,
            'manage_url': manage_url,
        }
        return render(
            request,
            page_template,
            context,
        )
    except ObjectDoesNotExist:
        subscribe_url = reverse(
            'django_simple_bulk_emailer:get_subscriptions',
        )
        page_template = f'{get_universal_page_directory()}/manage_subscriptions_error.html'
        context = {
            'subscribe_url': subscribe_url,
        }
        return render(
            request,
            page_template,
            context,
        )


def email_preview(request, list_slug, pk):
    if not request.user.has_perm('django_simple_bulk_emailer.change_bulkemail') \
            and not request.user.has_perm('django_simple_bulk_emailer.view_bulkemail'):
        raise PermissionDenied
    subscription = Subscription.objects.filter(
        list_slug=list_slug,
    ).first()
    if not subscription:
        raise Http404()
    else:
        email_class = subscription.get_email_class()
        try:
            email_instance = email_class.objects.get(
                pk=pk,
            )
        except (ObjectDoesNotExist, ValueError) as e:
            raise Http404()
        list_return = HttpResponseRedirect(
            reverse(
                f'admin:{email_instance._meta.app_label}_{email_instance._meta.model_name}_changelist'
            )
        )
        page_template = f'{subscription.email_directory}/email_template_html.html'
        basic_template = f'{get_universal_page_directory()}/bulk_email_preview.html'
        if request.method == "POST":
            if 'send_email' in request.POST:
                email_instance.sendable = True
                email_instance.sending = True
                email_instance.sent = True
                email_instance.save()
                return list_return
            if 'return_list' in request.POST:
                return list_return
        context = {
            'basic_template': basic_template,
            'email_instance': email_instance,
        }
        return render(
            request,
            page_template,
            context,
        )


def list_view(request, list_slug):
    subscription = Subscription.objects.filter(
        list_slug=list_slug,
        publicly_visible=True,
        use_pages=True,
    ).first()
    if not subscription:
        raise Http404()
    else:
        email_class = subscription.get_email_class()
        email_set = email_class.objects.filter(
            subscription_list=subscription,
            published=True,
        ).order_by(
            '-publication_date',
            '-created',
        )
        try:
            paginate = settings.EMAILER_PAGINATION
        except AttributeError:
            paginate = True
        if paginate:
            try:
                page_results = settings.EMAILER_PAGINATION_RESULTS
            except AttributeError:
                page_results = 10
            paginator = Paginator(email_set, page_results)
            page = request.GET.get('page')
            try:
                email_set = paginator.page(page)
            except PageNotAnInteger:
                email_set = paginator.page(1)
            except EmptyPage:
                email_set = paginator.page(paginator.num_pages)
        page_template = f'{subscription.page_directory}/list_view.html'
        subscribe_url = reverse(
            'django_simple_bulk_emailer:get_subscriptions',
        )
        context = {
            'subscription': subscription,
            'email_set': email_set,
            'subscribe_url': subscribe_url,
        }
        return render(
            request,
            page_template,
            context,
        )


def page_view(request, list_slug, year, month, day, pk, headline_slug, preview=False):
    subscription = Subscription.objects.filter(
        list_slug=list_slug,
        publicly_visible=True,
        use_pages=True,
    ).first()
    if not subscription:
        raise Http404()
    else:
        email_class = subscription.get_email_class()
        try:
            email_instance = email_class.objects.get(
                subscription_list=subscription,
                pk=pk,
            )
        except (ObjectDoesNotExist, ValueError) as e:
            raise Http404()
        if not preview and not email_instance.published:
            raise Http404()
        page_template = f'{subscription.page_directory}/page_view.html'
        context = {
            'email_instance': email_instance,
        }
        context_defaults_dict = {
            'default_image': 'EMAILER_DEFAULT_IMAGE',
            'default_type': 'EMAILER_DEFAULT_TYPE',
            'default_width': 'EMAILER_DEFAULT_WIDTH',
            'default_height': 'EMAILER_DEFAULT_HEIGHT',
            'default_alt': 'EMAILER_DEFAULT_ALT',
        }
        for key, value in context_defaults_dict.items():
            try:
                new_value = getattr(settings, value)
            except AttributeError:
                new_value = ''
            context.update({key: new_value})
        return render(
            request,
            page_template,
            context,
        )


def page_preview(request, list_slug, year, month, day, pk, headline_slug):
    if not request.user.has_perm('django_simple_bulk_emailer.change_bulkemail') \
            and not request.user.has_perm('django_simple_bulk_emailer.view_bulkemail'):
        raise PermissionDenied
    return page_view(request, list_slug, year, month, day, pk, headline_slug, preview=True)


def opened_email(request, pk, subscriber_key):
    try:
        email_tracker = EmailTracker.objects.get(
            pk=pk,
        )
        if email_tracker.json_data:
            dict_data = email_tracker.json_data
        else:
            dict_data = {}
        if subscriber_key not in dict_data:
            dict_data[subscriber_key] = [
                timezone.now().year,
                timezone.now().month,
            ]
            email_tracker.json_data = dict_data
            email_tracker.save()
    except (ObjectDoesNotExist, ValueError) as e:
        pass
    temp_handle = BytesIO()
    image_file = Image.new(
        'RGBA',
        (1, 1),
        (0, 0, 0, 0),
    )
    image_file.save(
        temp_handle,
        'png',
    )
    temp_handle.seek(0)
    image_data = temp_handle.read()
    return HttpResponse(
        image_data,
        content_type='image/png',
    )


def get_subscriber(email):
    return Subscriber.objects.get(
        subscriber_email=email,
    )


def new_subscriber(email):
    return Subscriber(
        subscriber_email=email,
        )


@csrf_exempt
def mc_sync(request):
    try:
        request_type = request.POST.get(
            'type',
            '',
        )
        email = request.POST.get(
            'data[email]',
            '',
        ).lower()
        old_email = request.POST.get(
            'data[old_email]',
            '',
        ).lower()
        new_email = request.POST.get(
            'data[new_email]',
            '',
        ).lower()
        first_name = request.POST.get(
            'data[merges][FNAME]',
            '',
        )
        last_name = request.POST.get(
            'data[merges][LNAME]',
            '',
        )
        mc_list = request.POST.get(
            'data[list_id]',
            '',
        )
        secret_key = request.GET.get('key', '')
        subscription = Subscription.objects.filter(
            mc_sync=True,
        ).filter(
            mc_list=mc_list,
        ).filter(
            secret_key=secret_key,
        ).first()
        if subscription:
            if request_type == 'upemail':
                try:
                    subscriber_old = get_subscriber(old_email)
                except ObjectDoesNotExist:
                    subscriber_old = None
                try:
                    subscriber_new = get_subscriber(new_email)
                except ObjectDoesNotExist:
                    subscriber_new = None
                if subscriber_old is not None:
                    if subscriber_new:
                        for subscription_item in subscriber_new.subscriptions.all():
                            subscriber_old.subscriptions.add(subscription_item)
                            subscriber_new.subscriptions.remove(subscription_item)
                        subscriber_new.delete()
                    subscriber_old.subscriber_email = new_email
                    subscriber_old.mc_email = new_email
                    subscriber_old.save()
                    subscriber_old.subscriptions.add(subscription)
                else:
                    if subscriber_new is None:
                        subscriber_new = new_subscriber(new_email)
                        subscriber_new.save()
                    subscriber_new.subscriptions.add(subscription)
            else:
                if request_type == 'unsubscribe' or request_type == 'cleaned':
                    try:
                        subscriber = get_subscriber(email)
                        subscriber.subscriptions.remove(subscription)
                    except ObjectDoesNotExist:
                        pass
                else:
                    try:
                        subscriber = get_subscriber(email)
                    except ObjectDoesNotExist:
                        subscriber = new_subscriber(email)
                    if first_name != '':
                        subscriber.first_name = first_name
                    if last_name != '':
                        subscriber.last_name = last_name
                    subscriber.save()
                    subscriber.subscriptions.add(subscription)
            secret_key_old = subscription.secret_key
            subscription.secret_key = ''
            subscription.save()
            site = Site.objects.get(
                id=settings.SITE_ID,
            )
            site_profile = SiteProfile.objects.filter(
                domain=site.domain,
            ).first()
            base_url = reverse(
                'django_simple_bulk_emailer:mc_sync',
            )
            url_old = f'{site_profile.protocol_domain()}{base_url}?key={secret_key_old}'
            url_new = f'{site_profile.protocol_domain()}{base_url}?key={subscription.secret_key}'
            try:
                from mailchimp3 import (
                    MailChimp,
                )
                from mailchimp3.mailchimpclient import (
                    MailChimpError,
                )
                client = MailChimp(
                    mc_api=subscription.mc_api,
                    mc_user=subscription.mc_user,
                )
                try:
                    webhooks = client.lists.webhooks.all(list_id=mc_list)['webhooks']
                    for hook in webhooks:
                        if hook['url'] == url_old:
                            hook_id = hook['id']
                            client.lists.webhooks.update(
                                list_id=mc_list,
                                webhook_id=hook_id,
                                data={
                                    'url': url_new,
                                }
                            )
                            break
                except MailChimpError:
                    pass
            except ImportError:
                pass
        else:
            return HttpResponse('INVALID CREDENTIALS')
    except IntegrityError:
        pass
    return HttpResponse('COMPLETED')

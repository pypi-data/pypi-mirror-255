from django.urls import path, include
from . import superfunctions, views

app_name="stela_control"

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('meta-data/', views.metaID, name="meta_data"),
    path('ig-data/', views.igID, name="ig_data"),
    path('meta-api/', views.metaAPI, name="meta_request"),
    path('test/', views.test, name="test"),
    path('validators/', views.validators, name="validators"),
    path('api-control/', views.StelaAPIView, name="api_view"),

    #Stela Dashboard
    path('console/newcomer', views.newcomer, name="newcomer"),
    path('console/home', views.console, name="console"),
    path('pro-stela/chats/', views.stelaChat, name="chats"),
    path('pro-stela/expert', views.stelaExpert, name="expert"),

    #access
    path('', views.loginstela, name='login'),
    path('logout/', views.logout_view, name="logout"),

    #Inbox
    path('content/inbox', views.contactMessage, name="inbox"), 
    
    #Support 
    path('support-center', views.supportCenter, name="support"),
    path('support-case/<int:id>', views.updateSupport, name="support-case"),

    #Comments
    path('comments-blog', views.commentsBlog, name="commentsBlog"),

    #jobs
    path('jobs', views.jobs, name="jobs"),

    #Emails
    path('email-marketing', views.emailMarketing, name="email-marketing"),
    
    #StelaContent
    path('dycontent', views.mainContent, name="main-content"),
    path('dycontent/main', views.siteMain, name="site-main"),
    path('dycontent/docs', views.siteDocs, name="site-docs"),
    path('dycontent/staff', views.staff, name="site-staff"),
    path('dycontent/stela-story', views.stelaStory, name="stela_story"),
    
    #inventory
    path('inventory-control/services', views.services, name="service"),
    path('inventory-control/products', views.products, name="products"),
    path('inventory-control/update-product/<int:id>', views.updateProduct, name="updateProduct"),
    path('inventory-control/resources', views.resources, name="resources"),

    #metaplatform
    path('marketing/business-suite', views.metaSuite, name="meta_business"),
    path('marketing/business-suite/<int:id>', views.metaDetail, name="meta_detail"),
    path('marketing/business-suite/<int:id>/content-pro', views.page, name="fb_page"),
    path('marketing/business-suite/<int:id>/analythics', views.pageAnalythics, name="page_insights"),
    path('marketing/<int:id>/icreative-actions/<int:ig>/', views.IcreativeActions, name="ic_actions"),
    path('marketing/business-suite/<int:id>/insight-creative/<int:ig>', views.insightCreative, name="increative"),
    path('marketing/business-suite/<int:id>/analyzer/<int:ig>', views.igAnalyzer, name="iganalyzer"),
    path('marketing/business-suite/fbmedia', views.fbmedia, name="fb_media"),
    path('marketing/business-suite/igmedia', views.igmedia, name="ig_media"),
    path('marketing/business-suite/ig-counter/<int:id>/', views.igCounter, name="ig_counter"),
    path('marketing/business-suite/ig-check/<int:id>/', views.igCheckPost, name="check_ig_post"),
    path('marketing/<int:id>/grid/<int:ig>/', views.grid, name="ig_grid"),
    
    #googlePlatform
    path('googleapis/auth', views.googleAuth, name="google_auth"),

    #orders
    path('booking-control', views.bookingControl, name="booking_control"),
    path('booking-control/<int:id>/', views.bookingDetail, name="booking_detail"),

    # #reviews
    path('reviews', views.reviews, name="reviews"),
    # path('update-review/<int:id>/', views.update_review, name="update_review"),
    # path('delete-review/', views.delete_reviews, name="delete_review"),
    # path('search-auto/review/', views.autocompleteReview, name="autocomplete_review"),
    
    #users
    path('users', views.users, name="users"),
    path('users-control/<int:id>/', views.users_control, name="users_control"),
    path('profile/<int:id>/', views.profile, name="update_user"),
    
    #email-events
    #path('store/send-email/order-confirmation/', views.send_order_confirm_store, name="email_order_confirm_store"),
    
    #stelaPayments
    path('payments/home', views.paymentsHome, name="homebrew"),
    path('payments/add-wallet', views.addWallet, name="addwallet"),
    path('payments/wallets', views.Wallets, name="wallets"),
    path('payments/withdrawals/', views.withdrawals, name="withdrawals"),
    #StelaBilling
    path('billings/home', views.stelaBilling, name="billing"),
    path('billings/new-bill/', views.createBill, name="bill_new"),
    path('billings/edit-bill/<int:id>', views.editBill, name="edit_billing"),
    path('billings/preview/<int:id>', views.previewBilling, name="previewBill"),
    path('billings/get-billing/<int:id>', views.get_billing, name="get_billing"),
    path('billings/bill-detail/<int:id>', views.get_invoice, name="get_invoice"),
    path('billings/recipt-detail/<int:id>', views.get_invoice, name="get_invoice"),
    path('billings/recipt-detail-ves/<int:id>', views.get_invoice_ves, name="get_invoice_ves"),
    
    #stela SuperFunctions
    path('validations/dynamic-forms/', superfunctions.dynamicForms, name="dynamic_forms"),
    path('validations/content/', superfunctions.contentData, name="content_data"),
    path('validations/docs/', superfunctions.docsData, name="docs_data"),
    path('validations/staff/', superfunctions.staffData, name="staff_data"),
    path('validations/stela-story/', superfunctions.stelaStoryData, name="stela_story_data"),
    path('validations/inventory/', superfunctions.inventoryData, name="inventory_data"),
    path('validations/stela-api/', superfunctions.requestAPI, name="api_data"),
    path('validations/billing/', superfunctions.billingData, name="billing_data"),
    path('validations/sendgrid/<int:id>/<int:ig>/', superfunctions.sendgridData, name="sendgrid_data"),
    path('validations/facebook/<int:id>/', superfunctions.sendgridData, name="sendgrid_data"),
    path('validations/instagram/<int:id>/<int:ig>/', superfunctions.sendgridData, name="sendgrid_data"),
    path('validations/accounts/', superfunctions.accountsData, name="accounts_data"),
    path('validations/suspend-account/', superfunctions.suspend_user, name="suspend_user"),
    path('validations/activate-user/', superfunctions.activate_user, name="activate_user"),
    path('validations/suspend-portal-account/', superfunctions.suspend_portal_user, name="suspend_portal_user"),
    path('validations/booking/', superfunctions.bookingData, name="booking_data"),
    path('validations/inputs/', superfunctions.inputsData, name="inputs_data"),
    path('validations/jobs/', superfunctions.jobApplication, name="jobs_data"),
    path('validations/handlers/', superfunctions.coreHandlers, name="handlers_data"),
    path('validations/render/', superfunctions.renderData, name="render_data"),
    path('validations/messages/', superfunctions.messageData, name="messages_data"),
    path('validations/youtube-playlist/', superfunctions.get_youtube_playlist_videos, name="playlist_data"),
    path('auth/password_reset_confirm/<uidb64>/<token>/', superfunctions.new_password_activate, name="password_reset_token"),
    path('auth/account/<uidb64>/<token>/', superfunctions.account_activate, name="account_token"),
 ]   
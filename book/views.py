from django.shortcuts import render,redirect,get_object_or_404
from .models import Book,Proof
from django.db.models import Q
import hashlib
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail


# Create your views here.

#redirection to event table
def payment_redirect(request):
    books=Book.objects.all()
    proofs=Proof.objects.all()
    return render(request, "book/event.html",{'books':books,
        'proofs':proofs
        })


#dashboard
def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect(schedule)
        else:
            return redirect(user_dashboard)


def user_dashboard(request):
    user_books=Proof.objects.filter(book__user=request.user)
    return render(request, "login/user_dashboard.html",{
                  "user_books":user_books})
    

def schedule(request):
    schedule='schedule'
    books=Book.objects.all()
    proofs=Proof.objects.all()
    return render(request, "login/admin_panel.html",
           {'books':books,
        'proofs':proofs,
        'schedule':schedule
        })

def payment(request):
    payment='payment'
    books=Book.objects.all()
    proofs=Proof.objects.all()
    return render(request, "login/admin_panel.html",
           {'books':books,
        'proofs':proofs,
        'payment':payment
        })

def event_status(request):
    event_status='event_status'
  
    books=Book.objects.all()
    proofs=Proof.objects.all()
    return render(request, "login/admin_panel.html",
           {'books':books,
        'proofs':proofs,
        'event_status':event_status
        })

def admin_setting(request):
    return render(request, 'login/admin_setting.html')
    
    

   


#store check in data of customer
def check_in(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            book_type = request.POST.get('book_type')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            payment_method = request.POST.get('payment_method')
            payment_type = request.POST.get('payment_type')

            overlapped_date=Book.objects.filter(
            Q(start_date__lte=end_date)&Q(end_date__gte=start_date))
        
            if overlapped_date.exists():
                return render(request, "book/book.html", {
                "error":"The Date overlapse"
            })

            new_booking = Book(
            user=request.user,
            book_type=book_type, start_date=start_date,
            end_date=end_date, payment_method=payment_method,
            payment_type=payment_type
        )
            new_booking.save()
            return redirect("payment_proof")
        return render(request, "book/book.html")
    else:
        return redirect("login")

#payment proof is store in database
def payment_proof(request):
    user=request.user
    try:
        if request.method == 'POST':
            img = request.FILES.get("img")
            book = Book.objects.filter(user=request.user).latest('id')
            amount = book.amount 
            Proof.objects.create(
                book=book,
                img=img,
                payment_status="Pending" 
            )
            messages.success(request, "Payment proof uploaded successfully!")



            #user notify
            send_mail(
            'Booking Confirmation at Milagrosa Happiness Private Resort',
            'Hello,\n\nWe are excited to let you know that your booking at Milagrosa Happiness Private Resort has been successfully received! '
            'Your payment is currently being processed and is expected to be approved within 1-3 business days.\n\n'
            'Once your payment is confirmed, we will send you a follow-up email with all the final details of your reservation'
            'Thank you for choosing Milagrosa Happiness Private Resort — we look forward to welcoming you soon for a relaxing and memorable stay!\n\n'
            'If you have any questions or need further assistance, please feel free to reply to this email or contact our customer support team.\n\n'
            'Best regards,\nMilagrosa Happiness Private Resort Team',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False)

          
            #admin notify
            send_mail(
            'New Booking Has Been Made',
            'Hello, We wanted to inform you that a new booking has been successfully made in the system. ',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_ADMIN],
            fail_silently=False
            )
            return redirect("index")
        else:
  
            book_last = Book.objects.filter(user=request.user).latest('id')
            amount = book_last.amount
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect("payment_proof")

    return render(request, "book/gcash.html", {'amount': amount})

#payment status change

def accept_payment(request, proof_id):
    proof=get_object_or_404(Proof, id=proof_id)
    user=proof.book.user
    proof.payment_status="approved"
    proof.save()
    send_mail(
    'Your Payment Has Been Approved! - Milagrosa Happiness Private Resort',
    f"""Hello {user.username if user.username else 'Guest'},

We are pleased to inform you that your payment for your booking at Milagrosa Happiness Private Resort has been successfully approved! Your reservation is now fully confirmed, and we are thrilled to welcome you soon.

Here’s your booking summary:
- Start Date: {proof.book.start_date.strftime('%B %d, %Y')}
- End Date: {proof.book.end_date.strftime('%B %d, %Y')}
- Booking Type: {proof.book.book_type}
- Total Amount Paid: ₱{proof.book.amount:,.2f}

For any questions, please contact us at reservations@milagrosaresort.com.

Thank you for choosing Milagrosa Happiness Private Resort!
""",
    settings.EMAIL_HOST_USER,  
    [user.email],
    fail_silently=False
)
    return redirect('approving')


def cancel_payment(request, proof_id):
    proof=get_object_or_404(Proof, id=proof_id)
    proof.payment_status="declined"
    proof.save()
    return redirect('approving')


def delete_book(request, id):
    book=get_object_or_404(Proof, id=id)
    book.delete()
    return redirect('user_dashboard')


#book status

def cancel_book(request,id):
    book=get_object_or_404(Book, id=id)
    user=book.user
    book.refund_status="Pending"
    book.save()
    send_mail(
        'Booking Cancellation Notice',
        f'Hello We have received your refund request ',
        f'at {user.email} Please Process the refund Request',
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_ADMIN],
        fail_silently=False
    )
    send_mail(
    'Your Refund Request Has Been Received',
    f'Hello {user.username},\n\nWe have received your refund request for your booking at Milagrosa Happiness Private Resort. '
    'Our team is now reviewing your request, and you can expect an update within 1-4 business days.\n\n'
    'If you have any questions or need further assistance, please feel free to reply to this email.\n\n'
    'Thank you for your patience and understanding.\n\nBest regards,\nMilagrosa Happiness Private Resort Team',
    settings.EMAIL_HOST_USER,
    [user.email], 
    fail_silently=False
)
    return redirect('user_dashboard')
    
#refund change status

def refund_complete(request, id):
    
    if not request.user.is_superuser:
        return redirect('index') 
    
    proof = get_object_or_404(Proof, id=id)
    booking = proof.book
    user = proof.book.user

    # Update the refund status
    booking.refund_status = "complete"
    booking.save()
    
    
    messages.success(request, "Refund marked as complete")
    
    send_mail(
    'Your Refund Has Been Successfully Processed',
    f'Hello {user.username},\n\nWe are pleased to inform you that your refund for your booking at Milagrosa Happiness Private Resort '
    'has been successfully processed and the amount has been transferred to your account. '
    'Please allow 1-3 business days for the transaction to reflect in your account, depending on your bank or payment provider.\n\n'
    'Thank you for your patience throughout this process. If you have any questions or need further assistance, '
    'please feel free to reply to this email or contact our support team.\n\n'
    'We hope to serve you again in the future!\n\nBest regards,\nMilagrosa Happiness Private Resort Team',
    settings.EMAIL_HOST_USER,
    [user.email],
    fail_silently=False
)

    return redirect('refund')



def policies(request):
    return render(request, "book/policies.html")
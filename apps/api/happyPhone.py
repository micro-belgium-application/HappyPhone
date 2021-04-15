from django.db import connection
from django.http import HttpResponse


# Ajouter descriptif des status erreur

def getDisplayPhone(request):
    phone_number = request.GET.get("phone", "unknown")
    if phone_number.isdigit():
        try:
            with connection.cursor() as cursor:

                sql = "exec [dbo].[HappyPhone_Global_Search_For_Phone_Display] @numPhone=%s"
                # sql = "SELECT @@version;"
                params = [phone_number]
                cursor.execute(sql, params)
                cursor.nextset()
                row = cursor.fetchone()[0]

            if row is None:
                return HttpResponse(phone_number, status=200)

            return HttpResponse(row, status=200)
        except:
            return HttpResponse('E:Server error', status=500)

    else:
        return HttpResponse('E:Phone number format', status=400)

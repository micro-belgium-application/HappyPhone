from django.db import connection
from django.http import HttpResponse


def getDisplayPhone(request):
    phone_number = request.GET.get("phone", "0")
    if phone_number.isdigit():
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

    else:
        return HttpResponse('Wrong entry type', status=500)
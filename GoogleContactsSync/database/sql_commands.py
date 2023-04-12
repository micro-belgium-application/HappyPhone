
PROCEDURE_GContactFeed = """
               DECLARE @out int;
               EXEC [dbo].[GContact_insert] @output=@out, @accountSrc=?, @gFeed=?, @lastUpdated=?, @lastSync=?, @fullname=?, @lastname=?, @name=?, @memo=?, @jobTitle=?, @company=?, @deleted=?, @raw_json=?, @etag=?;
               SELECT @out AS pk;
            """
PROCEDURE_GGroup = """ 
               DECLARE @out int;
               EXEC [dbo].[GGroup_update] @gFeed=?, @accountSrc=?, @name=?, @systemGroup=?, @lastUpdated=?, @lastSync=?, @deleted=? ;
               SELECT @out as pkGroup;
               """
PROCEDURE_GGroupContact = """
               EXEC [dbo].[GGroupContact_update] @idContact=?, @gFeedG=?, @accountSrc=?;
               """
PROCEDURE_delete_from_tables = """
               EXEC [dbo].[GDelete_from_tables] @idContact=?;
               """
PROCEDURE_GAddress = """ 
               DECLARE @out int;
               EXEC [dbo].[GAddress_update] @output=@out, @type=?, @street=?, @city=?, @region=?, @postcode=?, @country=?, @idContact=? ;
               SELECT @out as pkAddress ;
               """
PROCEDURE_GEmail = """
               DECLARE @out int ;
               EXEC [dbo].[GEmail_update] @output=@out, @email=?, @type=?, @idContact=? ;
               SELECT @out as pkEmail ;
               """
PROCEDURE_GNumPhone = """
               DECLARE @out int ;
               EXEC [dbo].[GNumPhone_update] @output=@out, @numPhone=?,  @type=?, @idContact=? ;
               SELECT @out as pkNumPhone ;
               """
PROCEDURE_GUserDefinedField = """
               DECLARE @out int ;
               EXEC [dbo].[GUserDefinedField_update] @output=@out, @idContact=?, @key=?, @value=? ;
               SELECT @out as pkUserDefinedField ;
               """

# New procedures

PROCEDURE_GPhoneNumbers = """
               DECLARE @out int ;
               EXEC [dbo].[PhoneNumbers_update] @output=@out, @rawPhone=?,  @canonicalForm=?, @integerForm=?, @bigIntegerForm=?, @type=?, @idGoogle=?, @idContact=?, @logs=? ;
               SELECT @out as pkNumPhone ;
               """
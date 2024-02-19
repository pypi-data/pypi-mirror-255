from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext


class SharePointUploader:

    @staticmethod
    def upload_file_to_sharepoint(url, username, password, folder_url, file_name, file_path):
        ctx_auth = AuthenticationContext(url)
        if ctx_auth.acquire_token_for_user(username, password):
            ctx = ClientContext(url, ctx_auth)
            web = ctx.web
            ctx.load(web)
            ctx.execute_query()
            print(f"Authentication successful: {web.properties['Title']}")

            with open(file_path, 'rb') as content_file:
                file_content = content_file.read()

            target_folder = ctx.web.get_folder_by_server_relative_url(
                folder_url)
            target_file = target_folder.upload_file(file_name, file_content)
            ctx.execute_query()
            print(f"File {file_name} has been uploaded to {folder_url}")
        else:
            print("Authentication failed")

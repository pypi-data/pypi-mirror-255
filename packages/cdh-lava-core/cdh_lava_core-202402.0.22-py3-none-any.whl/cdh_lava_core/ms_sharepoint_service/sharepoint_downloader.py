from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext


class SharePointDownloader:

    @staticmethod
    def download_file_from_sharepoint(url, username, password, file_url, download_path):
        ctx_auth = AuthenticationContext(url)
        if ctx_auth.acquire_token_for_user(username, password):
            ctx = ClientContext(url, ctx_auth)
            web = ctx.web
            ctx.load(web)
            ctx.execute_query()
            print(f"Authentication successful: {web.properties['Title']}")

            download_file = ctx.web.get_file_by_server_relative_url(file_url)
            ctx.load(download_file)
            ctx.execute_query()

            with open(download_path, 'wb') as local_file:
                local_file.write(download_file.read())
            print(f"File has been downloaded to {download_path}")

        else:
            print("Authentication failed")

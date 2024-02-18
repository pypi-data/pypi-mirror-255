from typing import Optional, Sequence

import pulumi
import pulumi_azure_native as azure
import pulumi_random


class DjangoDeployment(pulumi.ComponentResource):
    HEALTH_CHECK_PATH = "/health-check"

    def __init__(
        self,
        name,
        tenant_id: str,
        resource_group_name: pulumi.Input[str],
        vnet: azure.network.VirtualNetwork,
        pgsql_ip_prefix: str,
        appservice_ip_prefix: str,
        app_service_sku: azure.web.SkuDescriptionArgs,
        storage_account_name: str,
        cdn_host: Optional[str],
        opts=None,
    ):
        """
        Create a Django deployment.

        :param name: The name of the deployment, will be used to name subresources.
        :param tenant_id: The Entra tenant ID for the database authentication.
        :param resource_group_name: The resource group name to create the resources in.
        :param vnet: The virtual network to create the subnets in.
        :param pgsql_ip_prefix: The IP prefix for the PostgreSQL subnet.
        :param appservice_ip_prefix: The IP prefix for the app service subnet.
        :param app_service_sku: The SKU for the app service plan.
        :param storage_account_name: The name of the storage account. Should be unique across Azure.
        :param cdn_host: A custom CDN host name (optional)
        :param opts: The resource options
        """

        super().__init__("pkg:index:DjangoDeployment", name, None, opts)

        # child_opts = pulumi.ResourceOptions(parent=self)

        self._name = name
        self._tenant_id = tenant_id
        self._rg = resource_group_name
        self._vnet = vnet

        # Storage resources
        self._create_storage(account_name=storage_account_name)
        self._cdn_host = self._create_cdn(custom_host=cdn_host)

        # PostgreSQL resources
        self._create_database(ip_prefix=pgsql_ip_prefix)

        # Subnet for the apps
        self._app_subnet = self._create_subnet(
            name="app-service",
            prefix=appservice_ip_prefix,
            delegation_service="Microsoft.Web/serverFarms",
            service_endpoints=["Microsoft.Storage"],
        )

        # Create App Service plan that will host all websites
        self._app_service_plan = self._create_app_service_plan(sku=app_service_sku)

        # Create a pgAdmin app
        self._create_pgadmin_app()

    def _create_storage(self, account_name: str):
        # Create blob storage
        self._storage_account = azure.storage.StorageAccount(
            f"sa-{self._name}",
            resource_group_name=self._rg,
            account_name=account_name,
            sku=azure.storage.SkuArgs(
                name=azure.storage.SkuName.STANDARD_LRS,
            ),
            kind=azure.storage.Kind.STORAGE_V2,
            access_tier=azure.storage.AccessTier.HOT,
            allow_blob_public_access=True,
            public_network_access=azure.storage.PublicNetworkAccess.ENABLED,
            enable_https_traffic_only=True,
        )

    def _create_cdn(self, custom_host: Optional[str]) -> pulumi.Output[str]:
        """
        Create a CDN endpoint. If a host name is given, it will be used as the custom domain.
        Otherwise, the default CDN host name will be returned.

        :param custom_host: The custom domain (optional)
        :return: The CDN host name
        """

        # Put CDN in front
        cdn = azure.cdn.Profile(
            f"cdn-{self._name}",
            resource_group_name=self._rg,
            location="global",
            sku=azure.cdn.SkuArgs(
                name=azure.cdn.SkuName.STANDARD_MICROSOFT,
            ),
        )

        endpoint_origin = self._storage_account.primary_endpoints.apply(
            lambda primary_endpoints: primary_endpoints.blob.replace("https://", "").replace("/", "")
        )

        self._cdn_endpoint = azure.cdn.Endpoint(
            f"cdn-endpoint-{self._name}",
            resource_group_name=self._rg,
            location="global",
            is_compression_enabled=True,
            content_types_to_compress=[
                "application/javascript",
                "application/json",
                "application/x-javascript",
                "application/xml",
                "text/css",
                "text/html",
                "text/javascript",
                "text/plain",
            ],
            is_http_allowed=False,
            is_https_allowed=True,
            profile_name=cdn.name,
            origin_host_header=endpoint_origin,
            origins=[azure.cdn.DeepCreatedOriginArgs(name="origin-storage", host_name=endpoint_origin)],
            query_string_caching_behavior=azure.cdn.QueryStringCachingBehavior.IGNORE_QUERY_STRING,
        )

        pulumi.export("cdn_cname", self._cdn_endpoint.host_name)

        # Add custom domain if given
        if custom_host:
            azure.cdn.CustomDomain(
                f"cdn-custom-domain-{self._name}",
                resource_group_name=self._rg,
                profile_name=cdn.name,
                endpoint_name=self._cdn_endpoint.name,
                host_name=custom_host,
            )

            return custom_host
        else:
            # Return the default CDN host name
            return self._cdn_endpoint.host_name

    def _create_database(self, ip_prefix: str):
        # Create subnet for PostgreSQL
        subnet = self._create_subnet(
            name="pgsql",
            prefix=ip_prefix,
            delegation_service="Microsoft.DBforPostgreSQL/flexibleServers",
        )

        # Create private DNS zone
        dns = azure.network.PrivateZone(
            f"dns-pgsql-{self._name}",
            resource_group_name=self._rg,
            location="global",
            # The zone name must end with this to work with Azure DB
            private_zone_name=f"{self._name}.postgres.database.azure.com",
        )

        # Link the private DNS zone to the VNet in order to make resolving work
        azure.network.VirtualNetworkLink(
            f"vnet-link-pgsql-{self._name}",
            resource_group_name=self._rg,
            location="global",
            private_zone_name=dns.name,
            virtual_network=azure.network.SubResourceArgs(id=self._vnet.id),
            registration_enabled=False,
        )

        # Create PostgreSQL server
        self._pgsql = azure.dbforpostgresql.Server(
            f"pgsql-{self._name}",
            resource_group_name=self._rg,
            sku=azure.dbforpostgresql.SkuArgs(
                name="Standard_B2s",
                tier=azure.dbforpostgresql.SkuTier.BURSTABLE,
            ),
            version="16",
            auth_config=azure.dbforpostgresql.AuthConfigArgs(
                password_auth=azure.dbforpostgresql.PasswordAuthEnum.DISABLED,
                active_directory_auth=azure.dbforpostgresql.ActiveDirectoryAuthEnum.ENABLED,
                tenant_id=self._tenant_id,
            ),
            storage=azure.dbforpostgresql.StorageArgs(storage_size_gb=32),
            network=azure.dbforpostgresql.NetworkArgs(
                delegated_subnet_resource_id=subnet.id,
                private_dns_zone_arm_resource_id=dns.id,
            ),
            backup=azure.dbforpostgresql.BackupArgs(
                backup_retention_days=7,
                geo_redundant_backup=azure.dbforpostgresql.GeoRedundantBackupEnum.DISABLED,
            ),
        )

        pulumi.export("pgsql_host", self._pgsql.fully_qualified_domain_name)

    def _create_subnet(
        self, name, prefix, delegation_service: Optional[str] = None, service_endpoints: Sequence[str] = []
    ) -> azure.network.Subnet:
        """
        Generic method to create a subnet with a delegation.

        :param name: The name of the subnet
        :param prefix: The IP prefix
        :param delegation_service: The service to delegate to
        :param service_endpoints: The service endpoints to enable
        :return: The subnet
        """

        if delegation_service:
            delegation_service = azure.network.DelegationArgs(
                name=f"delegation-{name}-{self._name}",
                service_name=delegation_service,
            )

        service_endpoints = [azure.network.ServiceEndpointPropertiesFormatArgs(service=s) for s in service_endpoints]

        return azure.network.Subnet(
            f"subnet-{name}-{self._name}",
            resource_group_name=self._rg,
            virtual_network_name=self._vnet.name,
            address_prefix=prefix,
            delegations=[delegation_service],
            service_endpoints=service_endpoints,
        )

    def _create_app_service_plan(self, sku: azure.web.SkuDescriptionArgs) -> azure.web.AppServicePlan:
        # Create App Service plan
        return azure.web.AppServicePlan(
            f"asp-{self._name}",
            resource_group_name=self._rg,
            kind="Linux",
            reserved=True,
            sku=sku,
        )

    def _create_pgadmin_app(self):
        # The app itself
        app = azure.web.WebApp(
            f"app-pgadmin-{self._name}",
            resource_group_name=self._rg,
            server_farm_id=self._app_service_plan.id,
            virtual_network_subnet_id=self._app_subnet.id,
            identity=azure.web.ManagedServiceIdentityArgs(
                type=azure.web.ManagedServiceIdentityType.SYSTEM_ASSIGNED,
            ),
            https_only=True,
            site_config=azure.web.SiteConfigArgs(
                ftps_state=azure.web.FtpsState.DISABLED,
                linux_fx_version="DOCKER|dpage/pgadmin4",
                health_check_path="/misc/ping",
                app_settings=[
                    azure.web.NameValuePairArgs(name="DOCKER_REGISTRY_SERVER_URL", value="https://index.docker.io/v1"),
                    azure.web.NameValuePairArgs(name="DOCKER_ENABLE_CI", value="true"),
                    # azure.web.NameValuePairArgs(name="WEBSITE_HTTPLOGGING_RETENTION_DAYS", value="7"),
                    # pgAdmin settings
                    azure.web.NameValuePairArgs(name="PGADMIN_DISABLE_POSTFIX", value="true"),
                    azure.web.NameValuePairArgs(name="PGADMIN_AUTHENTICATION_SOURCES", value="['oauth2, 'internal']"),
                    azure.web.NameValuePairArgs(name="PGADMIN_OAUTH2_NAME", value="azure"),
                    azure.web.NameValuePairArgs(name="PGADMIN_DEFAULT_EMAIL", value="dbadmin@dbadmin.net"),
                    azure.web.NameValuePairArgs(name="PGADMIN_DEFAULT_PASSWORD", value="dbadmin"),
                ],
            ),
        )

        # Create a storage container for persistent data (SMB share)
        share = azure.storage.FileShare(
            f"share-pgadmin-{self._name}",
            resource_group_name=self._rg,
            account_name=self._storage_account.name,
            share_name="pgadmin",
        )

        # Mount the storage container
        azure.web.WebAppAzureStorageAccounts(
            f"app-pgadmin-mount-{self._name}",
            resource_group_name=self._rg,
            name=app.name,
            properties={
                "pgadmin-data": azure.web.AzureStorageInfoValueArgs(
                    account_name=self._storage_account.name,
                    access_key=self._get_storage_account_access_keys(self._storage_account)[0].value,
                    mount_path="/var/lib/pgadmin",
                    share_name=share.name,
                    type=azure.web.AzureStorageType.AZURE_FILES,
                )
            },
        )

        pulumi.export("pgadmin_url", app.default_host_name.apply(lambda host: f"https://{host}"))

    def _add_webapp_host(self, app: azure.web.WebApp, host: str, suffix: str):
        """
        Because of a circular dependency, we need to create the certificate and the binding in two steps.
        First we create a binding without a certificate,
        then we create the certificate and then we update the binding.

        The certificate needs the binding, and the binding needs the thumbprint of the certificate.

        See also: https://github.com/pulumi/pulumi-azure-native/issues/578

        :param app: The web app
        :param host: The host name
        :param suffix: A suffix to make the resource name unique
        """

        safe_host = host.replace(".", "-")

        try:
            # Retrieve the existing binding - this will throw an exception if it doesn't exist
            azure.web.get_web_app_host_name_binding(
                resource_group_name=app.resource_group,
                name=app.name,
                host_name=host,
            )

            # Create a managed certificate
            # This will work because the binding exists actually
            certificate = azure.web.Certificate(
                f"cert-{suffix}-{safe_host}",
                resource_group_name=self._rg,
                server_farm_id=app.server_farm_id,
                canonical_name=host,
                host_names=[host],
            )

            # Create a new binding, replacing the old one,
            # with the certificate
            azure.web.WebAppHostNameBinding(
                f"host-binding-{suffix}-{safe_host}",
                resource_group_name=self._rg,
                name=app.name,
                host_name=host,
                ssl_state=azure.web.SslState.SNI_ENABLED,
                thumbprint=certificate.thumbprint,
            )
        except Exception:
            # Create a binding without a certificate
            azure.web.WebAppHostNameBinding(
                f"host-binding-{suffix}-{safe_host}",
                resource_group_name=self._rg,
                name=app.name,
                host_name=host,
            )

    def _get_storage_account_access_keys(
        self, storage_account: azure.storage.StorageAccount
    ) -> Sequence[azure.storage.outputs.StorageAccountKeyResponse]:
        """
        Helper function to get the access keys for a storage account.

        :param storage_account: The storage account
        :return: The access keys
        """

        keys = azure.storage.list_storage_account_keys(
            resource_group_name=self._rg,
            account_name=storage_account.name,
        )

        return keys.keys

    def add_database_administrator(self, object_id: str, user_name: str):
        """
        Add an Entra ID as database administrator.

        :param object_id: The object ID of the user
        :param user_name: The user name (user@example.com)
        """

        azure.dbforpostgresql.Administrator(
            # Must be random but a GUID
            f"pgsql-admin-{user_name.replace('@', '_')}-{self._name}",
            resource_group_name=self._rg,
            server_name=self._pgsql.name,
            object_id=object_id,
            principal_name=user_name,
            principal_type=azure.dbforpostgresql.PrincipalType.USER,
            tenant_id=self._tenant_id,
        )

    def add_django_website(
        self,
        name: str,
        db_name: str,
        repository_url: str,
        repository_branch: str,
        website_hosts: list[str],
        django_settings_module: str,
        environment_variables: dict[str, str] = {},
    ) -> azure.web.WebApp:
        """
        Create a Django website with it's own database and storage containers.

        :param name: The reference for the website, will be used to name subresources.
        :param db_name: The name of the database to create.
        :param repository_url: The URL of the Git repository.
        :param repository_branch: The Git branch to deploy.
        :param website_hosts: The list of custom host names for the website.
        :param django_settings_module: The Django settings module to load.
        :param environment_variables: A dictionary of environment variables to set.
        """

        # Create a database
        db = azure.dbforpostgresql.Database(
            f"db-{name}",
            database_name=db_name,
            resource_group_name=self._rg,
            server_name=self._pgsql.name,
        )

        # Container for media files
        media_container = azure.storage.BlobContainer(
            f"storage-container-{name}-media-{self._name}",
            resource_group_name=self._rg,
            account_name=self._storage_account.name,
            public_access=azure.storage.PublicAccess.BLOB,
            container_name=f"{name}-media",
        )

        # Container for static files
        static_container = azure.storage.BlobContainer(
            f"storage-container-{name}-static-{self._name}",
            resource_group_name=self._rg,
            account_name=self._storage_account.name,
            public_access=azure.storage.PublicAccess.BLOB,
            container_name=f"{name}-static",
        )

        # Create a Django Secret Key (random)
        secret_key = pulumi_random.RandomString(f"django-secret-{name}-{self._name}", length=50)

        # Convert environment variables to NameValuePairArgs
        environment_variables = [
            azure.web.NameValuePairArgs(
                name=key,
                value=value,
            )
            for key, value in environment_variables.items()
        ]

        app = azure.web.WebApp(
            f"app-{name}-{self._name}",
            resource_group_name=self._rg,
            server_farm_id=self._app_service_plan.id,
            virtual_network_subnet_id=self._app_subnet.id,
            identity=azure.web.ManagedServiceIdentityArgs(
                type=azure.web.ManagedServiceIdentityType.SYSTEM_ASSIGNED,
            ),
            https_only=True,
            site_config=azure.web.SiteConfigArgs(
                always_on=True,
                health_check_path=self.HEALTH_CHECK_PATH,
                ftps_state=azure.web.FtpsState.DISABLED,
                python_version="3.12",
                # scm_type=azure.web.ScmType.EXTERNAL_GIT,
                linux_fx_version="PYTHON|3.12",
                app_settings=[
                    # Build settings
                    azure.web.NameValuePairArgs(name="SCM_DO_BUILD_DURING_DEPLOYMENT", value="true"),
                    azure.web.NameValuePairArgs(name="PRE_BUILD_COMMAND", value="cicd/pre_build.sh"),
                    azure.web.NameValuePairArgs(name="POST_BUILD_COMMAND", value="cicd/post_build.sh"),
                    azure.web.NameValuePairArgs(name="DISABLE_COLLECTSTATIC", value="true"),
                    azure.web.NameValuePairArgs(name="HEALTH_CHECK_PATH", value=self.HEALTH_CHECK_PATH),
                    # Django settings
                    # azure.web.NameValuePairArgs(name="DEBUG", value="true"),
                    azure.web.NameValuePairArgs(name="DJANGO_SETTINGS_MODULE", value=django_settings_module),
                    azure.web.NameValuePairArgs(name="DJANGO_SECRET_KEY", value=secret_key.result),
                    azure.web.NameValuePairArgs(name="DJANGO_ALLOWED_HOSTS", value=",".join(website_hosts)),
                    # Storage settings
                    azure.web.NameValuePairArgs(name="AZURE_STORAGE_ACCOUNT_NAME", value=self._storage_account.name),
                    azure.web.NameValuePairArgs(name="AZURE_STORAGE_CONTAINER_STATICFILES", value=static_container.name),
                    azure.web.NameValuePairArgs(name="AZURE_STORAGE_CONTAINER_MEDIA", value=media_container.name),
                    # CDN
                    azure.web.NameValuePairArgs(name="CDN_HOST", value=self._cdn_host),
                    # Database settings
                    azure.web.NameValuePairArgs(name="DB_HOST", value=self._pgsql.fully_qualified_domain_name),
                    azure.web.NameValuePairArgs(name="DB_NAME", value=db.name),
                    azure.web.NameValuePairArgs(name="DB_USER", value=f"{name}_managed_identity"),
                    *environment_variables,
                ],
            ),
        )

        # We need this to create the database role and grant permissions
        principal_id = app.identity.apply(lambda identity: identity.principal_id)
        pulumi.export(f"{name}_site_principal_id", principal_id)
        pulumi.export(f"{name}_site_db_user", f"{name}_managed_identity")

        # We need this to verify custom domains
        pulumi.export(f"{name}_site_domain_verification_id", app.custom_domain_verification_id)
        pulumi.export(f"{name}_site_domain_cname", app.default_host_name)

        for host in website_hosts:
            self._add_webapp_host(app=app, host=host, suffix=f"{name}-{self._name}")

        # To enable deployment from GitLab
        azure.web.WebAppSourceControl(
            f"app-{name}-sourcecontrol-{self._name}",
            resource_group_name=self._rg,
            name=app.name,
            repo_url=repository_url,
            branch=repository_branch,
            is_git_hub_action=False,
            is_manual_integration=True,
            is_mercurial=False,
        )

        # Where we can retrieve the SSH key
        pulumi.export(
            f"{name}_deploy_ssh_key_url", app.name.apply(lambda name: f"https://{name}.scm.azurewebsites.net/api/sshkey?ensurePublicKey=1")
        )

        # Find the role for Storage Blob Data Contributor
        storage_role = self._storage_account.id.apply(
            lambda scope: azure.authorization.get_role_definition(
                role_definition_id="ba92f5b4-2d11-453d-a403-e96b0029c9fe",
                scope=scope,
            )
        )

        # Grant the app access to the storage account
        azure.authorization.RoleAssignment(
            f"ra-{name}-storage",
            principal_id=principal_id,
            principal_type=azure.authorization.PrincipalType.SERVICE_PRINCIPAL,
            role_definition_id=storage_role.id,
            scope=self._storage_account.id,
        )

        # Create a CORS rule for this website
        # Add cors rules
        azure.storage.BlobServiceProperties(
            f"sa-{name}-blob-properties",
            resource_group_name=self._rg,
            account_name=self._storage_account.name,
            blob_services_name="default",
            cors=azure.storage.CorsRulesArgs(
                cors_rules=[
                    azure.storage.CorsRuleArgs(
                        allowed_headers=["*"],
                        allowed_methods=["GET", "OPTIONS", "HEAD"],
                        allowed_origins=[f"https://{host}" for host in website_hosts],
                        exposed_headers=["Access-Control-Allow-Origin"],
                        max_age_in_seconds=86400,
                    )
                ]
            ),
        )

        return app

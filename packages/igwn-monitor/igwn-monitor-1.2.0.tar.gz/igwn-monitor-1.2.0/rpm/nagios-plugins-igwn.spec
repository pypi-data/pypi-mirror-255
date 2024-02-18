%define srcname igwn-monitor
%define pkgname nagios-plugins-igwn
%define version 1.1.0
%define release 1
%define _plugindir %{_libdir}/nagios/plugins

# this build doesn't have a debug package
%global debug_package %{nil}

Name:      python-%{srcname}
Version:   %{version}
Release:   %{release}%{?dist}
Summary:   Nagios (Icinga) monitoring plugins for IGWN

License:   MIT
Url:       https://git.ligo.org/computing/monitoring/igwn-monitoring-plugins
Source0:   %pypi_source

Packager:  Duncan Macleod <duncan.macleod@ligo.org>
Vendor:    Duncan Macleod <duncan.macleod@ligo.org>

Prefix:    %{_prefix}

BuildRequires: python%{python3_pkgversion}-devel
BuildRequires: python%{python3_pkgversion}-pip
BuildRequires: python%{python3_pkgversion}-setuptools
BuildRequires: python%{python3_pkgversion}-setuptools_scm
BuildRequires: python%{python3_pkgversion}-wheel

%description
The igwn-monitoring-plugins project defines a Python library and set of
dependent monitoring plugin scripts developed for the International
Gravitational-Wave Observatory Network (IGWN).

# -- packages

# python3-igwn-monitor
%package -n python%{python3_pkgversion}-igwn-monitor
Summary: Python library for IGWN monitoring plugins
Requires: python%{python3_pkgversion}-ciecplib
Requires: python%{python3_pkgversion}-gssapi
Requires: python%{python3_pkgversion}-igwn-auth-utils >= 1.0.0
%if 0%{?rhel} != 0 && 0%{?rhel} < 9
Requires: python%{python3_pkgversion}-importlib-metadata
%endif
Requires: python%{python3_pkgversion}-requests
Requires: python%{python3_pkgversion}-requests-gssapi >= 1.2.2
%{?python_provide:%python_provide python%{python3_pkgversion}-igwn-monitor}
%description -n python%{python3_pkgversion}-igwn-monitor
The igwn-monitor library proides Python routines to support
custom Nagios (Icinga) monitoring plugins for IGWN.
%files -n python%{python3_pkgversion}-igwn-monitor
%doc README.md
%license LICENSE
%{python3_sitelib}/*

# nagios-plugins-igwn metapackage
%package -n %{pkgname}
Summary: Nagios (Icinga) monitoring plugins for IGWN (metapackage)
Requires: %{pkgname}-common = %{version}-%{release}
Requires: %{pkgname}-cvmfs = %{version}-%{release}
Requires: %{pkgname}-dqsegdb = %{version}-%{release}
Requires: %{pkgname}-docdb = %{version}-%{release}
Requires: %{pkgname}-gds = %{version}-%{release}
Requires: %{pkgname}-gitlab = %{version}-%{release}
Requires: %{pkgname}-gracedb = %{version}-%{release}
Requires: %{pkgname}-grafana = %{version}-%{release}
Requires: %{pkgname}-gwdatafind = %{version}-%{release}
Requires: %{pkgname}-gwosc = %{version}-%{release}
Requires: %{pkgname}-htcondor = %{version}-%{release}
Requires: %{pkgname}-json = %{version}-%{release}
Requires: %{pkgname}-kerberos = %{version}-%{release}
Requires: %{pkgname}-koji = %{version}-%{release}
Requires: %{pkgname}-mattermost = %{version}-%{release}
Requires: %{pkgname}-nds = %{version}-%{release}
Requires: %{pkgname}-scitoken = %{version}-%{release}
Requires: %{pkgname}-vault = %{version}-%{release}
Requires: %{pkgname}-xrootd = %{version}-%{release}
%description -n %{pkgname}
Extra Nagios (Icinga) monitoring plugins for IGWN.
This metapackage installs all of the IGWN monitoring plugins.
%files -n %{pkgname}
%doc README.md
%license LICENSE

# nagios-plugins-igwn-common
%package -n %{pkgname}-common
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-astropy
Requires: python%{python3_pkgversion}-gwdatafind
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Summary: IGWN Nagios (Icinga) common monitoring plugins
%description -n %{pkgname}-common
Common Nagios (Icinga) monitoring plugins for IGWN.
%files -n %{pkgname}-common
%doc README.md
%license LICENSE
%{_plugindir}/check_file_latency
%{_plugindir}/check_nmap
%{_plugindir}/check_rsync
%{_plugindir}/check_url

# nagios-plugins-igwn-cvmfs
%package -n %{pkgname}-cvmfs
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Requires: python%{python3_pkgversion}-requests
Summary: IGWN Nagios (Icinga) monitoring plugins for CVMFS
%description -n %{pkgname}-cvmfs
Nagios (Icinga) monitoring plugins to check CVMFS.
%files -n %{pkgname}-cvmfs
%doc README.md
%license LICENSE
%{_plugindir}/check_cvmfs*

# nagios-plugins-igwn-docdb
%package -n %{pkgname}-docdb
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-beautifulsoup4
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Requires: python%{python3_pkgversion}-requests
Summary: IGWN Nagios (Icinga) monitoring plugins for DocDB
%description -n %{pkgname}-docdb
Nagios (Icinga) monitoring plugins to check a DocDB instance.
%files -n %{pkgname}-docdb
%doc README.md
%license LICENSE
%{_plugindir}/check_docdb*

# nagios-plugins-igwn-dqsegdb
%package -n %{pkgname}-dqsegdb
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-dqsegdb2 >= 1.2.1
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for DQSegDB
%description -n %{pkgname}-dqsegdb
Nagios (Icinga) monitoring plugins to check a DQSegDB server.
%files -n %{pkgname}-dqsegdb
%doc README.md
%license LICENSE
%{_plugindir}/check_dqsegdb*

# nagios-plugins-igwn-gds
%package -n %{pkgname}-gds
Requires: gds-lsmp
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for GDS
%description -n %{pkgname}-gds
Nagios (Icinga) monitoring plugins to check a GDS
%files -n %{pkgname}-gds
%doc README.md
%license LICENSE
%{_plugindir}/check_partitions

# nagios-plugins-igwn-gitlab
%package -n %{pkgname}-gitlab
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for GitLab
%description -n %{pkgname}-gitlab
Nagios (Icinga) monitoring plugins to check a GitLab
%files -n %{pkgname}-gitlab
%doc README.md
%license LICENSE
%{_plugindir}/check_gitlab*

# nagios-plugins-igwn-gracedb
%package -n %{pkgname}-gracedb
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for GraCEDB
%description -n %{pkgname}-gracedb
Nagios (Icinga) monitoring plugins to check a GraCEDB server.
%files -n %{pkgname}-gracedb
%doc README.md
%license LICENSE
%{_plugindir}/check_gracedb*

# nagios-plugins-igwn-grafana
%package -n %{pkgname}-grafana
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for Grafana
%description -n %{pkgname}-grafana
Nagios (Icinga) monitoring plugins to check a Grafana server.
%files -n %{pkgname}-grafana
%doc README.md
%license LICENSE
%{_plugindir}/check_grafana*

# nagios-plugins-igwn-gwdatafind
%package -n %{pkgname}-gwdatafind
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-dqsegdb2 >= 1.2.1
Requires: python%{python3_pkgversion}-gwdatafind
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Requires: %{pkgname}-common = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for GWDataFind
%description -n %{pkgname}-gwdatafind
Nagios (Icinga) monitoring plugins to check a GWDataFind server.
%files -n %{pkgname}-gwdatafind
%doc README.md
%license LICENSE
%{_plugindir}/check_data_availability*
%{_plugindir}/check_gwdatafind*

# nagios-plugins-igwn-gwosc
%package -n %{pkgname}-gwosc
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for GWOSC
%description -n %{pkgname}-gwosc
Nagios (Icinga) monitoring plugins to check a GWOSC server.
%files -n %{pkgname}-gwosc
%doc README.md
%license LICENSE
%{_plugindir}/check_gwosc*

# nagios-plugins-igwn-htcondor
%package -n %{pkgname}-htcondor
Summary: IGWN Nagios (Icinga) monitoring plugins to check an HTCondor Pool
Requires: nagios-plugins
Requires: python3-condor
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
%description -n %{pkgname}-htcondor
Nagios (Icinga) monitoring plugin to check the status of an HTCondor Pool.
%files -n %{pkgname}-htcondor
%doc README.md
%license LICENSE
%{_plugindir}/check_htcondor*

# nagios-plugins-igwn-json
%package -n %{pkgname}-json
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-astropy
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
%if 0%{?rhel} != 0 && 0%{?rhel} < 9
Requires: python%{python3_pkgversion}-importlib-resources
%endif
Requires: python%{python3_pkgversion}-jsonschema
Requires: python%{python3_pkgversion}-pytz
Summary: IGWN Nagios (Icinga) monitoring plugin to parse JSON
%description -n %{pkgname}-json
Nagios (Icinga) monitoring plugins to parse remote JSON output
and format as a monitoring plugin.
%files -n %{pkgname}-json
%doc README.md
%license LICENSE
%{_plugindir}/check_json

# nagios-plugins-igwn-kerberos
%package -n %{pkgname}-kerberos
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Requires: python%{python3_pkgversion}-ldap3
Summary: IGWN Nagios (Icinga) monitoring plugins for Kerberos
%description -n %{pkgname}-kerberos
Nagios (Icinga) monitoring plugins for Kerberos.
%files -n %{pkgname}-kerberos
%doc README.md
%license LICENSE
%{_plugindir}/check_kdc*
%{_plugindir}/check_kerberos*

# nagios-plugins-igwn-koji
%package -n %{pkgname}-koji
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for Koji
%description -n %{pkgname}-koji
Nagios (Icinga) monitoring plugins to check a Koji server.
%files -n %{pkgname}-koji
%doc README.md
%license LICENSE
%{_plugindir}/check_koji*

# nagios-plugins-igwn-mattermost
%package -n %{pkgname}-mattermost
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for Mattermost
%description -n %{pkgname}-mattermost
Nagios (Icinga) monitoring plugins to check a Mattermost server.
%files -n %{pkgname}-mattermost
%doc README.md
%license LICENSE
%{_plugindir}/check_mattermost*

# nagios-plugins-igwn-nds
%package -n %{pkgname}-nds
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Requires: python%{python3_pkgversion}-nds2-client
Summary: IGWN Nagios (Icinga) monitoring plugins for NDS
%description -n %{pkgname}-nds
Nagios (Icinga) monitoring plugins to check an NDS(2) server.
%files -n %{pkgname}-nds
%doc README.md
%license LICENSE
%{_plugindir}/check_nds*


# nagios-plugins-igwn-scitoken
%package -n %{pkgname}-scitoken
Summary: IGWN Nagios (Icinga) monitoring plugins to check tokens
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-dateutil
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Requires: python%{python3_pkgversion}-pytz
Requires: python%{python3_pkgversion}-scitokens
%description -n %{pkgname}-scitoken
Nagios (Icinga) monitoring plugin to check for a SciToken and validate
its claims (aud, scope, and exp).
%files -n %{pkgname}-scitoken
%doc README.md
%license LICENSE
%{_plugindir}/check_gettoken
%{_plugindir}/check_scitoken*
%{_plugindir}/check_vault_token

# nagios-plugins-igwn-vault
%package -n %{pkgname}-vault
Summary: IGWN Nagios (Icinga) plugin to check a Hashicorp Vault
Requires: nagios-plugins
Requires: python3
Requires: python%{python3_pkgversion}-requests
%description -n %{pkgname}-vault
Nagios (Icinga) monitoring plugin to check a Hashicorp Vault instance.
%files -n %{pkgname}-vault
%doc README.md
%license LICENSE
%{_plugindir}/check_vault

# nagios-plugins-igwn-xrootd
%package -n %{pkgname}-xrootd
Requires: nagios-plugins
Requires: python%{python3_pkgversion}-igwn-monitor = %{version}-%{release}
Requires: python%{python3_pkgversion}-xrootd
Requires: %{pkgname}-common = %{version}-%{release}
Summary: IGWN Nagios (Icinga) monitoring plugins for XRootD
%description -n %{pkgname}-xrootd
Nagios (Icinga) monitoring plugins to check a XRootD server.
%files -n %{pkgname}-xrootd
%doc README.md
%license LICENSE
%{_plugindir}/check_xrd*
%{_plugindir}/check_xrootd*

# -- build steps

%prep
%autosetup -n %{srcname}-%{version}

%build
%py3_build_wheel

%install
# install the wheel as normal
%py3_install_wheel igwn_monitor-%{version}-*.whl
# then relocate all of the entry point scripts
mkdir -p %{buildroot}%{_plugindir}/
mv -v \
  %{buildroot}%{_bindir}/check_* \
  %{buildroot}%{_plugindir}/

# -- changelog

%changelog
* Fri Jan 26 2024 Duncan Macleod <duncan.macleod@ligo.org> - 1.1.0-1
- nagios-plugins-igwn-gds: new subpackage
- nagios-plugins-igwn-kerberos: add ldap3 requirement and bundle check_kerberos* plugins
- nagios-plugins-igwn-scitoken: add dateutil and tz requirements

* Tue Nov 28 2023 Duncan Macleod <duncan.macleod@ligo.org> - 1.0.1-2
- add requirements on 'common' for gwdatafind and xrootd packages

* Tue Sep 26 2023 Duncan Macleod <duncan.macleod@ligo.org> - 1.0.1-1
- update to 1.0.1
- add metapackage requirement on nagios-plugins-igwn-kerberos

* Thu Aug 31 2023 Duncan Macleod <duncan.macleod@ligo.org> - 1.0.0-1
- first packaged release of this project

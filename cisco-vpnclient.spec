# TODO:
# - /opt ??????
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)
#
%if !%{with kernel}
%undefine with_dist_kernel
%endif
%define		_rel	0.1
Summary:	Cisco Systems VPN Client
Summary(pl.UTF-8):	Klient VPN produkcji Cisco Systems
Name:		cisco-vpnclient
Version:	4.8.00.0490_k9
Release:	%{_rel}
License:	Commercial
Group:		Networking
Source0:	vpnclient-linux-4.8.00.0490-k9.tar.gz
# NoSource0-md5:	293b08509aa56d9b5ab9f536b0dea6f3
Source1:	vpnclient-linux-x86_64-4.8.00.0490-k9.tar.gz
# NoSource1-md5:	0f366eafd3a73823766e14b081591c0b
Source2:	cisco_vpnclient.init
NoSource:	0
NoSource:	1
# patchs - http://projects.tuxx-home.at/?id=cisco_vpn_client
Patch0:		%{name}-2.6.22.patch
URL:		http://www.cisco.com/en/US/products/sw/secursw/ps2308/tsd_products_support_series_home.html
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.22}
BuildRequires:	rpmbuild(macros) >= 1.379
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Cisco Systems VPN Client.

%description -l pl.UTF-8
Klient VPN produkcji Cisco Systems.

%package -n kernel-net-cisco_ipsec
Summary:	Cisco Systems VPN Client - kernel module
Summary(pl.UTF-8):	Klient VPN produkcji Cisco Systems - moduł jądra
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel}
Requires(post,postun):	/sbin/depmod
Provides:	cisco-vpnclient(kernel)

%description -n kernel-net-cisco_ipsec
Cisco Systems VPN Client - Linux kernel module.

%description -n kernel-net-cisco_ipsec -l pl.UTF-8
Klient VPN produkcji Cisco Systems - moduł jądra Linuksa.

%prep
%setup -q -T -c
%ifarch %{ix86}
tar -zxvf %{SOURCE0}
%endif
%ifarch %{x8664}
tar -zxvf %{SOURCE1}
%endif
%patch0 -p1

%build
%if %{with kernel}
%build_kernel_modules -m cisco_ipsec -C vpnclient
%endif

%install
rm -rf $RPM_BUILD_ROOT
#cd vpnclient
%if %{with kernel}
%install_kernel_modules -m cisco_ipsec -d misc
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sbindir}} \
	$RPM_BUILD_ROOT%{_sysconfdir}/opt/cisco-vpnclient/{Certificates,Profiles} \
	$RPM_BUILD_ROOT/opt/cisco-vpnclient/{bin,lib,include}

install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

install {cisco_cert_mgr,vpnclient,cvpnd,ipseclog} $RPM_BUILD_ROOT/opt/cisco-vpnclient/bin
install libvpnapi.so $RPM_BUILD_ROOT/opt/cisco-vpnclient/lib
install vpnapi.h $RPM_BUILD_ROOT/opt/cisco-vpnclient/include
install vpnclient.ini $RPM_BUILD_ROOT%{_sysconfdir}/opt/cisco-vpnclient

ln -sf /opt/cisco-vpnclient/bin/cisco_cert_mgr $RPM_BUILD_ROOT%{_sbindir}
ln -sf /opt/cisco-vpnclient/bin/vpnclient $RPM_BUILD_ROOT%{_sbindir}
ln -sf /opt/cisco-vpnclient/bin/ipseclog $RPM_BUILD_ROOT%{_sbindir}
ln -sf %{_sysconfdir}/opt/cisco-vpnclient $RPM_BUILD_ROOT%{_sysconfdir}/CiscoSystemsVPNClient
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add cisco-vpnclient
%service cisco-vpnclient restart

%preun
if [ "$1" = "0" ]; then
	%service cisco-vpnclient stop
	/sbin/chkconfig --del cisco-vpnclient
fi

%post	-n kernel%{_alt_kernel}-net-cisco_ipsec
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-net-cisco_ipsec
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc vpnclient/license.txt vpnclient/sample.pcf
%dir /opt/cisco-vpnclient
%dir /opt/cisco-vpnclient/bin
%dir /opt/cisco-vpnclient/lib
%dir /opt/cisco-vpnclient/include
%dir %{_sysconfdir}/opt/cisco-vpnclient
%dir %{_sysconfdir}/opt/cisco-vpnclient/Certificates
%dir %{_sysconfdir}/opt/cisco-vpnclient/Profiles
%attr(755,root,root) /opt/cisco-vpnclient/bin/*
%attr(755,root,root) %{_sbindir}/*
/opt/cisco-vpnclient/lib/*
/opt/cisco-vpnclient/include/*
%attr(755,root,root) %{_sysconfdir}/CiscoSystemsVPNClient
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/opt/cisco-vpnclient/vpnclient.ini
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%endif

%if %{with kernel}
%if %{without dist_kernel}
%files -n kernel%{_alt_kernel}-net-cisco_ipsec
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif
%endif

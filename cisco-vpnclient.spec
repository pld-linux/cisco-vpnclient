# TODO:
# - /opt ??????
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)
#
%if !%{with kernel}
%undefine with_dist_kernel
%endif
%define		_rel	0.1
Summary:	Cisco Systems VPN Client
Summary(pl):	Klient VPN produkcji Cisco Systems
Name:		cisco-vpnclient
Version:	4.7.00.0640_k9
Release:	%{_rel}
License:	Commercial
Group:		Networking
Source0:	vpnclient-linux-4.7.00.0640-k9.tar.gz
# NoSource0-md5:	435dd370208643e526623ddfca6e938a
Source1:	vpnclient-linux-x86_64-4.7.00.0640-k9.tar.gz
Source2:	cisco_vpnclient.init
NoSource:	0
NoSource:	1
URL:		http://www.cisco.com/en/US/products/sw/secursw/ps2308/tsd_products_support_series_home.html
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.0}
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Cisco Systems VPN Client.

%description -l pl
Klient VPN produkcji Cisco Systems.

%package -n kernel-net-cisco_ipsec
Summary:	Cisco Systems VPN Client - kernel module
Summary(pl):	Klient VPN produkcji Cisco Systems - modu³ j±dra
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Provides:	cisco-vpnclient(kernel)

%description -n kernel-net-cisco_ipsec
Cisco Systems VPN Client - Linux kernel module.

%description -n kernel-net-cisco_ipsec -l pl
Klient VPN produkcji Cisco Systems - modu³ j±dra Linuksa.

%package -n kernel-smp-net-cisco_ipsec
Summary:	Cisco Systems VPN Client - SMP kernel module
Summary(pl):	Klient VPN produkcji Cisco Systems - modu³ j±dra SMP
Release:	%{_rel}@%{_kernel_ver_str}
License:	Commercial
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Provides:	cisco-vpnclient(kernel)

%description -n kernel-smp-net-cisco_ipsec
Cisco Systems VPN Client - Linux SMP kernel module.

%description -n kernel-net-cisco_ipsec -l pl
Klient VPN produkcji Cisco Systems - modu³ j±dra Linuksa SMP.

%prep
%setup -q -T -c
%ifarch %{ix86}
tar -zxvf %{SOURCE0}
%endif
%ifarch %{x8664}
tar -zxvf %{SOURCE1}
%endif

%build
cd vpnclient
%if %{with kernel}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
%if !%{with dist_kernel}
	ln -sf %{_kernelsrcdir}/scripts
%endif
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	mv cisco_ipsec.ko cisco_ipsec-$cfg.ko
done
%endif

%install
rm -rf $RPM_BUILD_ROOT
cd vpnclient

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc

install cisco_ipsec-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/cisco_ipsec.ko
%if %{with smp} && %{with dist_kernel}
install cisco_ipsec-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/cisco_ipsec.ko
%endif
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

%post	-n kernel-net-cisco_ipsec
%depmod %{_kernel_ver}

%postun -n kernel-net-cisco_ipsec
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-cisco_ipsec
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-net-cisco_ipsec
%depmod %{_kernel_ver}smp

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
%files -n kernel-net-cisco_ipsec
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-cisco_ipsec
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
%endif

#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine with_dist_kernel
%endif

Summary:	Cisco Systems VPN Client
Name:		cisco_vpnclient
Version:	4.6.00.0045_k9
Release:	0.1
License:	Commercial
Vendor:		Cisco Systems
Group:		Networking
Source0:	vpnclient-linux-4.6.00.0045-k9.tar.gz
Source1:	%{name}.init
URL:		http://www.cisco.com
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.0}
BuildRequires:	rpmbuild(macros) >= 1.153
Requires:	cisco_vpnclient(kernel)
ExclusiveArch:	%{ix86}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_mandir		%{_prefix}/man

%description
Cisco Systems VPN Client

%package -n kernel-net-cisco_ipsec
Summary:	Cisco Systems VPN Client - kernel module
Release:	%{_rel}@%{_kernel_ver_str}
License:	Commercial
Vendor:		Cisco Systems
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Provides:	cisco_vpnclient(kernel)

%description -n kernel-net-cisco_ipsec
Cisco Systems VPN Client

%package -n kernel-smp-net-cisco_ipsec
Summary:	Cisco Systems VPN Client - kernel module (smp)
Release:	%{_rel}@%{_kernel_ver_str}
License:	Commercial
Vendor:		Cisco Systems
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Provides:	cisco_vpnclient(kernel)

%description -n kernel-smp-net-cisco_ipsec
Cisco Systems VPN Client (smp)

%prep
%setup -q -n vpnclient

%build
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
%if %{without dist_kernel}
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
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

install -d $RPM_BUILD_ROOT%{_sbindir}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/opt/cisco-vpnclient
install -d $RPM_BUILD_ROOT%{_sysconfdir}/opt/cisco-vpnclient/Certificates
install -d $RPM_BUILD_ROOT%{_sysconfdir}/opt/cisco-vpnclient/Profiles

install -d $RPM_BUILD_ROOT/opt/cisco-vpnclient/bin
install -d $RPM_BUILD_ROOT/opt/cisco-vpnclient/lib
install -d $RPM_BUILD_ROOT/opt/cisco-vpnclient/include

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
/sbin/chkconfig --add cisco_vpnclient
if [ -f /var/lock/subsys/cisco_vpnclient ]; then
        /etc/rc.d/init.d/cisco_vpnclient restart >&2
else
        echo "Run '/etc/rc.d/init.d/cisco_vpnclient start' to start vpnclient support." >&2
fi

%preun
if [ "$1" = "0" ]; then
        if [ -f /var/lock/subsys/cisco_vpnclient ]; then
                /etc/rc.d/init.d/cisco_vpnclient stop >&2
        fi
        /sbin/chkconfig --del cisco_vpnclient >&2
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
%doc license.txt sample.pcf
%dir /opt/cisco-vpnclient
%dir /opt/cisco-vpnclient/bin
%dir /opt/cisco-vpnclient/lib
%dir /opt/cisco-vpnclient/include
%dir %{_sysconfdir}/opt/cisco-vpnclient
%dir %{_sysconfdir}/opt/cisco-vpnclient/Certificates
%dir %{_sysconfdir}/opt/cisco-vpnclient/Profiles
%attr(755,root,root) /opt/cisco-vpnclient/bin/*
%attr(755,root,root) %{_sbindir}/*
%attr(644,root,root) /opt/cisco-vpnclient/lib/*
%attr(644,root,root) /opt/cisco-vpnclient/include/*
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

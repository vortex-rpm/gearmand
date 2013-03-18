
Name:           gearmand
Version:        1.1.2
Release:        2%{?dist}.vortex
Summary:        A distributed job system
Vendor:		Vortex RPM

Group:          System Environment/Daemons
License:        BSD
URL:            http://www.gearman.org
Source0:	https://launchpad.net/gearmand/1.2/%{version}/+download/gearmand-%{version}.tar.gz
Source1:        gearmand.init
Source2:        gearmand.sysconfig
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libevent-devel, boost-devel, libmemcached-devel

%if 0%{?el5}
BuildRequires:  e2fsprogs-devel 
%else
BuildRequires:  libuuid-devel
%endif

Requires(pre):   shadow-utils
Requires(post):  chkconfig
Requires(preun): chkconfig, initscripts
Requires:        procps

%description
Gearman provides a generic framework to farm out work to other machines
or dispatch function calls to machines that are better suited to do the work.
It allows you to do work in parallel, to load balance processing, and to
call functions between languages. It can be used in a variety of applications,
from high-availability web sites to the transport for database replication.
In other words, it is the nervous system for how distributed processing
communicates.


%package -n libgearman-devel
Summary:        Development headers for libgearman
Requires:       pkgconfig, libgearman = %{version}-%{release}
Group:          Development/Libraries
Requires:       libevent-devel

%description -n libgearman-devel
Development headers for %{name}

%package -n libgearman
Summary:        Development libraries for gearman
Group:          Development/Libraries


%description -n libgearman
Development libraries for %{name}


%prep
%setup -q

%build
%configure  \
    --disable-static \
    --disable-rpath \
    --without-mysql \
    --with-libmemcached

#sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
#sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
install -p -D -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/gearmand
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/gearmand
mkdir -p %{buildroot}/var/run/gearmand


%clean
rm -rf %{buildroot}


%pre
getent group gearmand >/dev/null || groupadd -r gearmand
getent passwd gearmand >/dev/null || \
        useradd -r -g gearmand -d / -s /sbin/nologin \
        -c "Gearmand job server" gearmand
exit 0

%post
if [ $1 -eq 1 ]; then
        /sbin/chkconfig --add gearmand
fi

%preun
if [ $1 -eq 0 ]; then
        /sbin/service gearmand stop >/dev/null 2>&1 || :
        /sbin/chkconfig --del gearmand
fi


%post -n libgearman -p /sbin/ldconfig
%postun -n libgearman -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc ChangeLog README
%dir %attr(755,gearmand,gearmand) /var/run/gearmand
%dir %attr(755,gearmand,gearmand) %{_localstatedir}/log/gearmand
%config(noreplace) %{_sysconfdir}/sysconfig/gearmand
%{_sbindir}/gearmand
%{_bindir}/gearman
%{_bindir}/gearadmin
%{_initrddir}/gearmand


%files -n libgearman-devel
%defattr(-,root,root,-)
%doc ChangeLog README
%dir %{_includedir}/libgearman
%{_includedir}/libgearman*
%{_libdir}/pkgconfig/gearmand.pc
%{_libdir}/libgearman*.so
%{_libdir}/libgearman*.la

%files -n libgearman
%defattr(-,root,root,-)
%doc ChangeLog README
%{_libdir}/libgearman.so.*
%{_libdir}/libgearman*.so.*

%changelog
* Mon Mar 18 2013 Ilya Otyutskiy <ilya.otyutskiy@icloud.com> - 1.1.2-2.vortex
- Create logdir.
- Rebuild with libmemcached support.

* Fri Oct 26 2012 Ilya A. Otyutskiy <sharp@thesharp.ru> - 1.1.2-1.vortex
- Update to 1.1.2.

* Fri Aug 24 2012 Ilya A. Otyutskiy <sharp@thesharp.ru> - 0.21-1.vortex
- Update to 0.21.

* Tue Apr 17 2012 Tom Callaway <spot@fedoraproject.org> - 0.14-3.2
- drop explicit gperftools Requires

* Wed Apr  4 2012 Tom Callaway <spot@fedoraproject.org> - 0.14-3.1
- rebuild against gperftools

* Thu Feb 24 2011 BJ Dierkes <wdierkes@rackspace.com> - 0.14-3
- Only build with tcmalloc on selected archs (i386/ppc on el5,
  and i686 only on el6) based on google-perftools availability
  in the Koji build repos.

* Fri Feb 04 2011 BJ Dierkes <wdierkes@rackspace.com> - 0.14-2
- Adding support for EPEL 5/6
- Added optional support for libmemcached
- Added optional support for tcmalloc (google-perftools)

* Fri Feb 04 2011 BJ Dierkes <wdierkes@rackspace.com> - 0.14-1
- Latest sources from upstream.  Full changelog available from:
  https://launchpad.net/gearmand/trunk/0.14

* Wed Oct 06 2010 Remi Collet <fedora@famillecollet.com> - 0.13-3
- rebuild against new libmemcached

* Wed May 05 2010 Remi Collet <fedora@famillecollet.com> - 0.13-2
- rebuild against new libmemcached

* Wed Apr 07 2010 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.13-1
- Upstream released new version

* Fri Feb 19 2010 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.12-1
- Upstream released new version

* Wed Feb 17 2010 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.11-2
- Add BR on libtool

* Tue Feb 16 2010 Oliver Falk <oliver@linux-kernel.at> 0.11-1
- Update to latest upstream version (#565808)
- Add missing Req. libevent-devel for libgearman-devel (#565808)
- Remove libmemcache patch - should be fixed in 0.11

* Sun Feb 07 2010 Remi Collet <fedora@famillecollet.com> - 0.9-3
- patch to detect libmemcached

* Sun Feb 07 2010 Remi Collet <fedora@famillecollet.com> - 0.9-2
- rebuilt against new libmemcached

* Fri Jul 31 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.9-1
- Upstream released new version

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.8-1
- Upstream released new version
- Enable libmemcached backend

* Mon Jun 22 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.7-1
- Upstream released new version

* Mon Jun 22 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.6-3
- Don't build with tcmalloc on sparc64

* Sun May 24 2009 Peter Lemenkov <lemenkov@gmail.com> 0.6-2
- Fixed issues, reported in https://bugzilla.redhat.com/show_bug.cgi?id=487148#c9

* Wed May 20 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.6-1
- Upstream released new version

* Mon Apr 27 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.5-1
- Upstream released new version
- Cleanups for review (bz #487148)

* Wed Feb 25 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.3-2
- Add init script

* Sat Feb 07 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.3-1
- Initial import


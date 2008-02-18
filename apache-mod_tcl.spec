#Module-Specific definitions
%define mod_name mod_tcl
%define mod_conf 27_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	1.0.1
Release:	%mkrel 4
Group:		System/Servers
License:	Apache License
URL:		http://tcl.apache.org/mod_tcl/
Source0:	%{mod_name}-%{version}.tar.gz
Source1:	%{mod_conf}
Source2:	test_script.tm
Patch0:		mod_tcl-fix-wild_name
Requires:	tcl >= 8.4.5
BuildRequires:	tcl >= 8.4.5
BuildRequires:	tcl-devel >= 8.4.5
Requires(pre):	tcl >= 8.4.5
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_tcl includes a Tcl interpreter into an Apache web servers memory space,
thus combining Tcl and Apache web server together. This allows Apache to run
Tcl scripts natively without having to reload a Tcl interpreter every time the
script is run. The Tcl scripts are cached in the Tcl interpreter until the
script file modification time changes or Apache web server is restarted. Tcl
scripts using mod_tcl execute much faster than traditional CGI scripts because
they can avoid the initialization penalties that traditional CGI scripts incur
each time they are executed. mod_tcl only needs to initialize an interpreter
once at Apache web server startup. Additionally mod_tcl exports the Apache API
which allows a programmer to have complete control over http requests that CGI
scripts can not provide.

%prep

%setup -q -n %{mod_name}-%{version}
%patch0

cp %{SOURCE2} test_script.tm
cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

cp tcl_core.c %{mod_name}.c 

# use stuff availble to determine stuff... :-)
. %{_libdir}/tclConfig.sh

#%{_sbindir}/apxs -c -I%{_includedir} -Wl,-ltcl8.3 -DHAVE_TCL_H %{mod_name}.c tcl_cmds.c tcl_misc.c
%{_sbindir}/apxs -c -I%{_includedir} -Wl,-ltcl${TCL_MAJOR_VERSION}.${TCL_MINOR_VERSION} -DHAVE_TCL_H %{mod_name}.c tcl_cmds.c tcl_misc.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS INSTALL NEWS README test_script.tm
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_var}/www/html/addon-modules/*



%define bname	geronimo
%define mstone	M2

%define _without_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define section	free

Name:		geronimo-specs
Version:	1.0
Release:	3.4.M2%{?dist}
Epoch:		0
License:	ASL 2.0
Group:		Development/Libraries
BuildRequires:	jpackage-utils >= 0:1.5
BuildRequires:	mx4j >= 0:2.0.1
BuildRequires:	apache-tomcat-apis
BuildRequires:	java-devel
Requires:	mx4j >= 0:2.0.1
Requires:	apache-tomcat-apis
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
%if %{gcj_support}
# libgcj aot-compiled native libraries
BuildRequires:	java-gcj-compat-devel >= 1.0.31
Requires(post):	java-gcj-compat >= 1.0.31
Requires(postun):java-gcj-compat >= 1.0.31
%else
BuildArch:	noarch
%endif

Summary:	Geronimo J2EE server J2EE specifications
URL:		http://geronimo.apache.org
Source0:	%{bname}-%{version}-%{mstone}-src.tar.gz


%description
Geronimo is Apache's ASF-licenced J2EE server project.
These are the J2EE-Specifications

%package compat
Group:		Development/Libraries
Summary:	Compatibility package for %{name}
Requires:	%{name} = %{version}-%{release}
Provides:	ejb = 0:2.1
Provides:	j2ee-connector = 0:1.5
Provides:	j2ee-deployment = 0:1.1
Provides:	j2ee-management = 0:1.0
Provides:	jacc = 0:1.0
Provides:	jms = 0:1.1
Provides:	jta = 0:1.0.1

%description compat
Fedora-specific package to make %{name} look like the
individual JPackages of the specifications we provide.

%prep
%setup -q -n geronimo-%{version}-%{mstone}
chmod -R go=u-w *

%build
# Force Java 5 (GCJ) as this code will not build on Java 6
# due to API differences (-source and -target only solve syntax problems)
export JAVA_HOME=/usr/lib/jvm/java-1.5.0
export PATH=$JAVA_HOME/bin:$PATH

mkdir -p build/lib
for spec in \
  ejb-2.1 \
  j2ee-connector-1.5 \
  j2ee-deployment-1.1 \
  j2ee-jacc-1.0 \
  j2ee-management-1.0 \
  jms-1.1 \
  jta-1.0.1B; do
    name=`echo $spec | sed 's:-[^-]*$::'`
    srcdir=specs/$name/src/java
    classdir=build/classes/$name
    mkdir -p $classdir
    jarfile=build/lib/spec-$spec.jar
    case $name in
    j2ee-jacc)
	CLASSPATH=$(build-classpath apache-tomcat-apis/tomcat-servlet2.4-api)
	export CLASSPATH
	;;
    j2ee-management)
	CLASSPATH=$(build-classpath mx4j/mx4j-jmx):build/lib/spec-ejb-2.1.jar
	export CLASSPATH
	;;
    *)
	unset CLASSPATH
    esac

    find $srcdir -name '*.java' | xargs javac  \
	-source 1.4 -target 1.4 -d $classdir || exit 1
	
    mkdir -p $classdir/META-INF
    cp -a LICENSE.txt $classdir/META-INF
    jar cf $jarfile -C $classdir .
done

%install
rm -rf $RPM_BUILD_ROOT

install -d -m 0755 $RPM_BUILD_ROOT%{_javadir}/%{bname}
for jar in build/lib/*.jar; do
    base=`basename $jar .jar`
    install -m 0644 $jar $RPM_BUILD_ROOT%{_javadir}/%{bname}/$base-rc2.jar
    ln -s $base-rc2.jar $RPM_BUILD_ROOT%{_javadir}/%{bname}/$base.jar

    compat=`echo $base | sed 's:^spec-\(.*\)-[^-]*$:\1:'`
    [ $compat = j2ee-jacc ] && compat=jacc
    ln -s %{bname}/$base.jar $RPM_BUILD_ROOT%{_javadir}/$compat.jar
done

%if %{gcj_support}
aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%if %{gcj_support}
%{_bindir}/rebuild-gcj-db
%endif

%postun
%if %{gcj_support}
%{_bindir}/rebuild-gcj-db
%endif

%files
%defattr(-,root,root,-)
%doc LICENSE.txt NOTICE.txt
%{_javadir}/%{bname}
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

%files compat
%defattr(-,root,root,-)
%{_javadir}/*.jar

%changelog
* Mon Feb 08 2010 Jeff Johnston <jjohnstn@redhat.com> - 0:1.0-3.4.M2
- Switch Requires/BuildRequires to use apache-tomcat-apis instead of
  servletapi5

* Tue Jan 12 2010 Jeff Johnston <jjohnstn@redhat.com> - 0:1.0-3.3.M2
- Resolves: #523218
- Switch package to default to noarch.

* Fri Jan 08 2010 Jeff Johnston <jjohnstn@redhat.com> - 0:1.0-3.2.M2
- Resolves: #523218
- Force java source and target to 1.4.

* Fri Jan 08 2010 Jeff Johnston <jjohnstn@redhat.com> - 0:1.0-3.1.M2
- Resolves: #553768
- Fix rpmlint warnings.

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.0-2.M2
- drop repotag

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:1.0-1.M2.2jpp.12
- Autorebuild for GCC 4.3

* Mon Aug 21 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.0-0.M2.2jpp.12
- Rebuild

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:1.0-0.M2.2jpp_11fc
- Rebuilt

* Thu Jul 13 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.0-0.M2.2jpp_10fc
- Reenable s390 s390x ppc64 excluded due to eclipse

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0:1.0-0.M2.2jpp_9fc
- rebuild

* Wed Mar  8 2006 Rafael Schloming <rafaels@redhat.com> - 0:1.0-0.M2.2jpp_8fc
- excluded s390[x] and ppc64 due to eclipse

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0:1.0-0.M2.2jpp_7fc
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0:1.0-0.M2.2jpp_6fc
- rebuilt for new gcc4.1 snapshot and glibc changes

* Wed Dec 21 2005 Jesse Keating <jkeating@redhat.com> 0:1.0-0.M2.2jpp_5fc
- rebuilt again

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Jul 22 2005 Gary Benson <gbenson at redhat.com> 0:1.0-0.M2.2jpp_4fc
- Switch to aot-compile-rpm.
- Also build jta.
- Build on ia64, ppc64, s390 and s390x.

* Wed Jun 29 2005 Gary Benson <gbenson at redhat.com> 0:1.0-0.M2.2jpp_3fc
- Add dependency on the main package to the compatibility subpackage.

* Mon Jun 27 2005 Gary Benson <gbenson at redhat.com> 0:1.0-0.M2.2jpp_2fc
- BC-compile.

* Wed Jun 15 2005 Gary Benson <gbenson at redhat.com> 0:1.0-0.M2.2jpp_1fc
- Build into Fedora.

* Fri Jun  3 2005 Gary Benson <gbenson at redhat.com>
- Only build the bits that we need, and don't use Maven to do it.
- Add a compatibility subpackage to provide dependencies.
- Add NOTICE file as per Apache License version 2.0.

* Thu Feb 03 2005 Ralph Apel <r.apel at r-apel.de> 0:1.0-0.M2.2jpp
- Process project.xml files with saxon
- Don't tamper with $HOME
- Don't use build-jar-repository: [xyz].jar will not work with geronimo deploy

* Fri Oct 08 2004 Ralph Apel <r.apel at r-apel.de> 0:1.0-0.M2.1jpp
- Upgrade to M2

* Thu Sep 30 2004 Ralph Apel <r.apel at r-apel.de> 0:1.0-0.M1.1jpp
- First JPackage build


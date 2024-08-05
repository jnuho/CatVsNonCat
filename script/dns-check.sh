#!/bin/bash

telnet -c pas.CatVsNonCat.net 443 2>&1 < /dev/null | grep Connected
telnet -c mqtt.CatVsNonCat.net 1883 2>&1 < /dev/null | grep Connected
telnet -c xmpp.CatVsNonCat.net 5223 2>&1 < /dev/null | grep Connected
telnet -c cwmp.CatVsNonCat.net 7548 2>&1 < /dev/null | grep Connected
telnet -c cdn.CatVsNonCat.net 7551 2>&1 < /dev/null | grep Connected
telnet -c data.CatVsNonCat.net 10443 2>&1 < /dev/null | grep Connected

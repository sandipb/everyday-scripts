=================================================
Sharing your laptop internet connection over wifi
=================================================

Configuration from `Vivek's blog post`_.

Four pieces of configuration:

1. ``hostapd`` configuration.
2. ``dhcpd`` configuration.
3. ``iptables`` configuration.
4. Interface configuration

Apart from the configurations given here in the repo, there is a wrapper script
which runs the whole set of services involved.

..    _Vivek's blog post:http://exain.wordpress.com/2011/03/31/making-a-wifi-hotspot-access-point-using-linux-wifi-lan-cardusb-adapter/

.. vim:nospell:ts=4:sw=4:tw=80:ai:fo+=n

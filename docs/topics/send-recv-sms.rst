So you want to build an SMS Service
======================================

Before setting up your SMS service, consider a few questions:

* Do you have technical staff and just want to try out an SMS service on a trial basis? Or do you want something robust from the start? This will determine whether you begin your exploration with a tethered phone/GSM modem or start looking immediately at SMS gateways.
* Do you need to offer your service via a) a shortcode, or b) is a regular phone number sufficient? If you want a shortcode, which mobile operators do you need to support? Do you need or expect your service to expand to multiple countries? Acquiring a shortcode is a time-consuming process, which needs to be persued individually with each operator in each country.
* If a longcode is sufficient, do you need to minimize cost to your end users? This determines whether you need to support a local number or whether you can work with international SMS gateways and international numbers.

To implement an SMS service, you can take the following approaches:

Set up a GSM Modem
=====================

This can be as simple as tethering a mobile phone to a laptop. More commonly, you'll purchase a dedicated GSM modem (which has better performance than a regular mobile phone) and attach it to a server somewhere. In the modem you'll place a local GSM-enabled SIM card, run the application on your server, and you're done.

**Pros:**

* Easy and fast to setup

**Cons:**

* Not a good long-term solution. Managing a GSM modem requires more knowledge than just managing traditional servers on a network, and most small or non-technical organizations will not have the capacity to ensure 99% uptime. This may be a viable solution for a larger organization that already hosts its own web servers and has dedicated technical staff.
* Shortcode not possible

Local SMS Gateway
===================

If you can find a reliable SMS gateway locally, this may be your best option, as they can provide local numbers, facilitate the acquisition of local short codes, and ideally provide competitive prices. Whether this is easy varies from country to ountry. In many countries, it is difficult and time-consuming to find a local provider who is timely and reliable.

**Con:**

* Typically local gateways are in the best position to facilitate acquisition of local shortcodes among multiple mobile operators

International SMS Gateway
===========================

There are many reputable international SMS gateways, although their service and availability within a particular country can vary greatly and should always be tested before launch.

**Pros:**

* Can provide strong technical infrastructre and volume discounts

**Cons:**

* Texting an international number is more expensive for end users
* Send text messages internationally can be expensive
* Shortcode not possible

Host a local SIM with an international SMS gateway
====================================================

One common solution we use is to take a local SIM card from a given country, enable roaming, and then ship it to an international SMS gateway. This gives us many benefits of the above two solutions without the drawbacks.

**Pros:**

* Users can text a local number cheaply
* Can provide strong technical infrastructre and volume discounts

**Cons:**

* Depends on the roaming infrastructure for a given network
* Shortcode not possible

Partnering with a Telecom Operator
======================================

Most SMS services are offered through third-party SMS gateways, whose business involves making it easier for third parties to offer services via SMS. Although it is rare, from time to time an organization can be lucky enough to form a strong partnership directly with a telecom operator.

**Pros**

* Can tap in directly to local telecom infrastructure. Less chance of messages being lost.
* Strong partnership with telco can result in other significant benefits, such as discounts, additional services, and better accounting/reporting.

**Cons**

* Telcos tend to be larger, often international organizations, and like any such organization, can move very slowly.
* Most SMS services are not large enough to warrant the attention of large telcos.
* If a shortcode is needed, still need to negotiate these with other telcos, either directly or through a gateway service.

Terminology
===============

**Gateway:** A gateway is a web service which provides access to particular services. A website can interface with an SMS gateway over the internet in order to send and recieve SMS.
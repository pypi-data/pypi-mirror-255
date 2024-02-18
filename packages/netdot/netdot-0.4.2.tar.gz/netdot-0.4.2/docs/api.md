# Reference Documentation

> The documentation below is a verbatim copy of the ['RESTful API docs' from the NetDot User Guide](https://github.com/cvicente/Netdot/blob/master/doc/manual/netdot-manual.html) (as of June 27, 2022).
>
> Hence, this document starts arbitrarily at section "7."

<h1 id="restful-interface"><span class="header-section-number">7</span> RESTful Interface</h1>
<p>The RESTful interface allows programmatic access to the Netdot database over the HTTP/HTTPS protocol. At this moment, all objects are formatted in XML using the XML::Simple Perl module. In the future, Netdot may support other formats, such as YAML or JSON.</p>
<h2 id="generic-restful-resources"><span class="header-section-number">7.1</span> Generic RESTful resources</h2>
<ul>
<li>The REST interface is available using the following URL (or similar, depending on your Apache configuration):</li>
</ul>
<pre><code>https://myserver.mydomain.com/netdot/rest/</code></pre>
<p>This should load the Netdot::REST class and return something like:</p>
<pre><code>Netdot/1.0 REST OK.</code></pre>
<ul>
<li>Generic RESTful resources to be acted upon represent Netdot objects and are part of the request URI. For example, in this URI:</li>
</ul>
<pre><code>http://myserver.mydomain.com/netdot/rest/device/1</code></pre>
<p>the resource is "device/1", which for a GET request, will return the contents of Device id 1.</p>
<ul>
<li>Using the following URI with a GET request:</li>
</ul>
<pre><code>http://myserver.mydomain.com/netdot/rest/device</code></pre>
<p>this interface will return the contents of all Device objects in the database.</p>
<ul>
<li>You can also specify certain search filters to limit the scope of a GET request:</li>
</ul>
<pre><code>http://myserver.mydomain.com/netdot/rest/device?sysname=host1</code></pre>
<p>This will perform a search and return all devices whose sysname field is 'host1'.</p>
<ul>
<li>The special keyword <code>meta_data</code> instead of an object ID will provide information about the object's class:</li>
</ul>
<pre><code>http://myserver.mydomain.com/netdot/rest/device/meta_data</code></pre>
<ul>
<li>An existing resource can be updated by using the 'POST' method with relevant parameters. For example, a POST request to the following URI:</li>
</ul>
<pre><code>URL: http://netdot.localdomain/rest/device/1
POST: {sysname=&gt;'newhostname'}</code></pre>
<p>will update the 'sysname' field of the Device object with id 1 to be "newhostname".</p>
<ul>
<li>Similarly, a new object can be created with a POST request. However, in this case the object id must be left out:</li>
</ul>
<pre><code>URL: http://netdot.localdomain/rest/person
POST: {firstname=&gt;'John', lastname=&gt;'Doe'}</code></pre>
<ul>
<li>Specific objects can be deleted by using the 'DELETE' HTTP method.</li>
</ul>
<h2 id="special-purpose-rest-resources"><span class="header-section-number">7.2</span> Special-purpose REST resources</h2>
<h3 id="resthost"><span class="header-section-number">7.2.1</span> /rest/host</h3>
<p>The special resource '/rest/host' provides a simplified interface for manipulating DNS and DHCP records. We will illustrate its usage with the following examples:</p>
<h4 id="retrieving-host-data-http-get"><span class="header-section-number">7.2.1.1</span> Retrieving host data (HTTP GET)</h4>
<ul>
<li>Retrieve all RR (DNS) objects</li>
</ul>
<pre><code>http://netdot.localdomain/netdot/rest/host</code></pre>
<ul>
<li>Retrieve all RR objects within given zone</li>
</ul>
<pre><code>http://netdot.localdomain/netdot/rest/host?zone=localdomain</code></pre>
<ul>
<li>Retrieve RR name "foo" and its related records</li>
</ul>
<pre><code>http://netdot.localdomain/netdot/rest/host?name=foo</code></pre>
<ul>
<li>Retrieve RR id 1 and all related records</li>
</ul>
<pre><code>http://netdot.localdomain/netdot/rest/host?rrid=1</code></pre>
<ul>
<li>Retrieve all Ipblock objects within given subnet</li>
</ul>
<pre><code>http://netdot.localdomain/netdot/rest/host?subnet=192.168.1.0/24</code></pre>
<h4 id="creating-new-records-http-post."><span class="header-section-number">7.2.1.2</span> Creating new records (HTTP POST).</h4>
<ul>
<li>Create new A record named 'host1' using next available address in given subnet (note: do not specify an object ID):</li>
</ul>
<pre><code>URL:  http://netdot.localdomain/netdot/rest/host
POST: {name='host1', subnet=&gt;'192.168.1.0/24'}</code></pre>
<h4 id="updating-existing-records-http-post"><span class="header-section-number">7.2.1.3</span> Updating existing records (HTTP POST)</h4>
<ul>
<li>Requires passing rrid or ipid. Rename host with RR id=2</li>
</ul>
<pre><code>URL:  http://netdot.localdomain/netdot/rest/host?rrid=2
POST: {name=&gt;'newname'}</code></pre>
<ul>
<li>Update DHCP scope ethernet for Ipblock with id=3</li>
</ul>
<pre><code>URL:  http://netdot.localdomain/netdot/rest/host?ipid=2
POST: {ethernet=&gt;'DEADDEADBEEF'}</code></pre>
<h4 id="deleting-records-http-delete"><span class="header-section-number">7.2.1.4</span> Deleting records (HTTP DELETE)</h4>
<ul>
<li>Delete hostname with RR id 3 (also frees IP)</li>
</ul>
<pre><code>http://netdot.localdomain/netdot/rest/host?rrid=3</code></pre>
<h3 id="restdevinfo"><span class="header-section-number">7.2.2</span> /rest/devinfo</h3>
<p>This special REST resource can be used to retrieve extensive information about every device in the database using a single GET request. The returned data structure is the same one used by the NAGIOS exporter class.</p>
<h3 id="restupdatedev"><span class="header-section-number">7.2.3</span> /rest/updatedev</h3>
<p>This special REST resource can be used to import devices into Netdot, as an alternative to using SNMP discovery. It accepts only POST requests. An example using the Perl client library can be found in the Netdot source, at:</p>
<pre><code>import/update_dev_rest.pl</code></pre>
<h2 id="restful-interface-authorization"><span class="header-section-number">7.3</span> RESTful Interface Authorization</h2>
<p>All user types can interact with the RESTful interface as long as they are granted permissions to do so. However only Admin users can edit or delete objects using generic REST resources. Operators and regular users can view generic resources but can only edit or delete them using specific-purpose resources such as 'rest/host'.</p>
<h2 id="client-module-on-cpan"><span class="header-section-number">7.4</span> Client module on CPAN</h2>
<p>A convenient module is provided via CPAN for use in Perl scripts that need to access Netdot's REST interface. The module name is Netdot::Client::REST. It can be installed by doing something like this:</p>
<p>If you are on a Debian-based system:</p>
<div class="sourceCode"><pre class="sourceCode bash"><code class="sourceCode bash"><span class="kw">~</span># <span class="kw">apt-get</span> install libnetdot-client-rest-perl</code></pre></div>
<p>or</p>
<div class="sourceCode"><pre class="sourceCode bash"><code class="sourceCode bash"><span class="kw">~</span># <span class="kw">cpan</span>
<span class="kw">&gt;install</span> Netdot::Client::REST</code></pre></div>
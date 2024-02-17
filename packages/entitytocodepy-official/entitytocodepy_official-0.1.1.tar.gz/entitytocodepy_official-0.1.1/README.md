<h1>Entity to code py</h1>
<h2>!!!WARNING!!! mathetc FUNCTIONS NOT AVAILIBLE</h2>

Version | 0.0.1 | 0.1.0  
--- | --- | --- 
Stable | yes | NO 


<h2>New feats</h2>
<h3>0.1.1 </h3>
<p><b>SO FILE BUG DETECTION, AS OF NOW, MODULE WITH VERSIONS 0.1.0 - Latest is UNUSABLE</b></p>
<h3>0.1.0 </h3>
<p><b>Binomials and Quadratic Calculations</b></p>
<h3>0.0.1 </h3>
<p><b>First with add_one()</b></p>

<h2>Usage</h2>
<h3>1) Installation</h3>

    pip install entitytocodepy_official==x.y.z
    pip install entitytocodepy_official==0.1.0


<h3>2) Importing to your python script</h3>

    from entitytocodepy import main

<h3>3) Using, here's a sample function</h3>

    main.add_one(1)

Output

    2

<h2>Methods</h2>
<h3>Quadratics (0.1.0 +)</h3>

Import

    from entitytocodepy import mathetc
Use

    mathetc.Roots(1,3,2)


<h3>Factorials (0.1.0 +)</h3>

Import

    from entitytocodepy import mathetc
Use

    mathetc.Factorial(4)


<h3>Binomials  (0.1.0 +)</h3>

Note: This is for finding singular terms in an expansion of (1+x)^n, eg: find the term of x^5 in (1+x)^7, here R (2nd param) == 5 and N = 7

Import

    from entitytocodepy import mathetc
Use

    mathetc.Binomialterm(7,5)

<h3>add_one (0.0.1 +)</h3>

Import

    from entitytocodepy import main
Use

    main.add_one(1)

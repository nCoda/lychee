.. _lychee_mei:

Lychee-MEI (LMEI)
=================

Lychee-MEI (LMEI) is the internal document format Lychee uses. LMEI restricts MEI to allow faster
and safer encoding. The LMEI restrictions are changing as development continues.


File Management
---------------

- Every MEI ``<section>`` is kept in its own file, to ease version control.
- Clients are therefore encouraged to use sections generously.
- An "all_files" MEI file holds references to all sections and metadata, in an arbitrary order.
- A "score" MEI file holds cross-references to "active" section files, in score order.
- Every LMEI file MUST include a ``@version`` attribute from the Lychee namespace on the root
  element. This will be the three-part version number of the Lychee version that saved the file.
  For example:

.. sourcecode:: xml

    <section xmlns:ly="https://lychee.ncodamusic.org" ly:version="0.3.2">
        <!-- musical content -->
    </section>


Others
------

- Use semantic @xml:id values as described below.
- The ``<multiRest>`` element isn't allowed; on conversion from MEI to Lychee-MEI, convert into
  multiple ``<mRest>`` elements.
- ``<mRest>`` elements must have a @dur attribute (and @dots if relevant).
- The ``<dot>`` element is forbidden in favour of @dot attributes. (We may need ``<dot>`` when
  dealing with particular repertoire or critical editions, later, but for now it's an
  unnecessary complication to support).
- When the @accid attribute appears on an element, the @accid.ges attribute must be used too. Using
  @accid.ges doesn't require @accid, however.


Spanners
--------

- The ``<tupletSpan>``, ``<beamSpan>``, ``<slur>``, and other elements that may refer to spanner
  objects with @startid and @endid, and are therefore inherently ambiguous and error-prone, must
  always use the @plist attribute to eliminate this ambiguity.
- Spanners that may be encoded as either an element containing other elements (like ``<tuplet>``)
  or as a pointing element (like ``<tupletSpan>``) must use the pointing version.
- Spanner elements must be sibling elements to the element indicated by its @startid attribute,
  and the spanner must precede the @startid element.
- The @plist attribute must include all child elements, not just immediate children (so in a
  nested tuplet, the highest-level ``<tupletSpan>`` will have in its @plist all of the notes/rests
  in that and any contained ``<tupletSpan>`` elements.
- Collectively, these restrictions eliminate the need for a multiple-pass parser.
- For a spanner that contains another spanner, the element defining the inner spanner must
  appear in the document *after* the element defining the outer spanner. This is implied in the
  previous rules, but specified more clearly here for consistency.
- Both @num and @numbase are required on every ``<tupletSpan>``.


"n" Attributes
--------------

- For containers that require an @n attribute, the values must be enumerated from 1, incremented
  by 1, and start with the top-most or left-most sub-container, as applicable.
- Therefore the first ``<section>`` will have ``@n="1"``, the next ``@n="2"``, and so on. An
  "inactive" ``<section>``, not part of the current "score," should either have ``@n="0"`` or no
  @n attribute at all.
- Therefore the top-most ``<staff>`` will have ``@n="1"``, the next ``@n="2"``, and so on.
- Therefore the ``<layer>`` with the "upper voice" will have ``@n="1"``, the "lower voice"
  ``@n="2"``, a subsequent "upper voice" ``@n="3"``, and so on (the goal being that "upper"
  voices with upward-pointing stems will have odd values of @n, and "lower" voices with
  downward-pointing stems will have even values of @n).
- Implication: when a sub-container is added or removed from a container (e.g., a ``<layer>``
  removed from  a ``<staff>``) the @n values of following sub-containers must be adjusted. This
  maintains the predictability of the "incremented by 1" stipulation.
- Additionally, the @n attribute of an element must equal the @n attribute of the corresponding
  element in other contexts (e.g., the principal flute's ``<staff>`` should be ``@n="1"`` in every
  ``<measure>``). This appears to create missing @n values, for example if an instrument does not
  appear in a particular ``<section>``. However, it allows us to assume that, if an @n value is
  missing in a context, the absence signifies an "empty" value. If @n values could be assigned
  arbitrarily, a missing @n value would not necessarily mean anything.
- Every ``<staffDef>`` element must have an @n attribute that is the same as the corresponding
  ``<staff>`` element(s).
- These rules specify extra precision for which standard MEI would require attributes like @prev
  and @next. Therefore the LMEI-to-MEI converter should add those attributes in order to allow
  proper round-trip conversion.


Nesting of Measures and Staves
------------------------------

This restriction is notable for being the only incompatibility between MEI and LMEI. Lychee-MEI
reverses the nesting order for ``<staff>`` and ``<measure>`` elements compared to MEI. The LMEI
document hierarchy looks like this:

.. sourcecode:: xml

    <section>
        <staff>
            <measure>  <!-- optional -->
                <layer/>
            </measure>
        </staff>
    </section>

There are two principal reasons we use this nesting order.

#. It more closely reflects the document hierarchy used in other formats, such as LilyPond, MusicXML,
   music21, and others. Conversion between these formats is faster when LMEI uses the same hierarchy.
#. It allows greater consistency between mensural and non-mensural representations. In standard MEI,
   converting a piece between mensural and non-mensural representations would require a significant
   change to the document hierarchy. With the measure-inside-staff nesting of LMEI, the change is
   less dramatic.

The second point, about converting between mensural and non-mensural representations, may seem like
an esoteric item of concern only to contemporary composers. However, this is about (non-)mensural
*representations*, not *scores*. Every score coming from LilyPond, for example, necessarily uses a
non-mensural representation because LilyPond syntax has no means to encode measures. Verovio, on the
other hand, currently requires ``<measure>`` elements in its input. We predict therefore that
converting between mensural and non-mensural representations will happen often.


ScoreDef and StaffDef
---------------------

- To the fullest extent possible, every ``<staffDef>`` must appear within a ``<scoreDef>``.
- Also as much as possible, both elements must only appear as the first element within a
  ``<section>``. It may not always be possible to abide by this rule, so exceptions may be
  clarified in the future.
- Every ``<staffDef>`` element must have an @n attribute that is the same as the corresponding
  ``<staff>`` element(s).


Semantic XML IDs
----------------

The @xml:id attribute of musical elements contained within a ``<section>`` must use the following
scheme to encode the element's position within the document hierarchy.

- Every element has a seven-digit "element ID."
- The @xml:id concatenates the element IDs for the section, staff, measure, and layer that contain
  the element. Each portion is separated with a hyphen. Each element ID is preceded by a single-letter
  reminder of its tag.
- If an element is a section, staff, measure, or layer, its place in the @xml:id is marked with "me".
- The element IDs of missing or irrelevant hierarchic elements are omitted.
- The generic ``@xml:id`` is ``@xml:id="SX-sX-mX-lX-eX"``, where ``X`` is an element ID.

Consider this example:

.. sourcecode:: xml

    <section xml:id="Sme-s-m-l-e1234567">
        <staff xml:id="S1234567-sme-m-l-e8974095">
            <measure xml:id="S1234567-s8974095-mme-l-e8290395">
                <layer xml:id="S1234567-s8974095-m8290395-lme-e7389825">
                    <note xml:id="S1234567-s8974095-m8290395-l7389825-e7290542"/>
                </layer>
                <slur xml:id="S1234567-s8974095-m8290395-l-e3729884"/>
            </measure>
        </staff>
    </section>

.. note:: This poses a unique problem for conversion to and from proper MEI documents where the
    document hierarchy may be different. We have yet to determine how to handle this situation.


Cross-References with Files
---------------------------

Lychee shall maintain a file called ``all_files.mei`` in which cross-reference links are kept for
all other MEI files in the repository. These cross-references use the ``<ptr>`` element.

- The @target attribute holds a URL to the other file, relative to ``all_files.mei``
- @targettype may be ``"section"``, ``"score"``, or ``"head"``, as appropriate.
- @xlink:actuate shall be ``"onRequest"``.
- @xlink:show shall be ``"embed"``.

.. sourcecode:: xml

    <meiCorpus>
        <meiHead>
            <ptr targettype="head" target="meihead.xml" xlink:actuate="onRequest" xlink:show="embed"/>
        </meiHead>
        <mei>
            <ptr targettype="score" target="score.xml" xlink:actuate="onRequest" xlink:show="embed"/>
            <ptr targettype="section" target="Sme-s-m-l-e4837298.mei" xlink:actuate="onRequest" xlink:show="embed"/>
            <ptr targettype="section" target="Sme-s-m-l-e9376275.mei" xlink:actuate="onRequest" xlink:show="embed"/>
            ...
        </mei>
    </meiCorpus>

.. note:: I'm not entirely sure this is valid MEI. If it's not, we should change the LMEI
    specification here to follow MEI if possible.


.. _mei_headers:

MEI Headers
-----------

These limitations apply to child elements of ``<meiHead>``.

- All title parts must be contained in a single ``<title>`` element. Use of the @type attribute is
  mandatory, with the possible values being those suggested by the MEI Guidelines: main, subordinate,
  abbreviated, alternative, translated, uniform. This means every ``<meiHead>`` element contains at
  least two ``<title>`` elements.
- The ``<respStmt>`` element contains ``<persName>`` elements referring to Lychee users.
  Contributors who have not used Lychee (or a Lychee client application) should be identified
  only with a more specific child element in the ``<titleStmt>``.
- The ``<persName>`` in ``<respStmt>`` should use child elements with @type="full", @type="given",
  @type="other", and @type="family" attributes to encode name parts. Use as many as possible,
  but only with values provided specifically by end users. That is, if a user provides only their
  full name, it should not be automatically encoded as parts; likewise, if a user only provides
  their name in parts, it should not be automatically encoded as a full name. This reduces the
  possibility of inadvertently using an incorrect name.
- A ``<persName>`` element may contain a ``<ptr>`` that links to a an externally-hosted image to be
  used as an avatar representing that person. In this case:

  - The ``@targettype`` attribute MUST be "avatar".
  - The ``@target`` attribute MUST be an HTTPS or HTTP URL to the image.
  - The ``@mimetype`` attribute MUST be a MIME type as specified in `RFC 2046`_ or omitted.
  - The ``@xlink:actuate`` attribute MUST be "none" or omitted.
  - The ``@xlink:show`` attribute MUST be "none" or omitted.

- The @xml:id for header elements should be some sort of UUID-like value, and should not follow
  the semantic @xml:id scheme used for musical elements. However, this value must be an NCName, and
  must therefore start with a letter.
- If the arranger, author, composer, editor, funder, librettist, lyricist, or sponsor elements
  identify someone who is also represented in the ``<respStmt>``, then the ``<persName>`` in
  the specific identifier should use a @nymref attribute with the @xml:id value of the
  ``<persName>`` in the ``<respStmt>``.

.. _`RFC 2046`: https://tools.ietf.org/html/rfc2046


Metadata Currently Supported by Lychee
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following document excerpt shows all the metadata fields that Lychee will support. Only the
fields with a ``<!-- required -->`` comment must be in the ``<meiHead>`` of every Lychee-MEI
document. They are therefore produced by the :func:`~lychee.document._empty_head` with placeholder
values.

Additional metadata will very likely be added in the future.

.. sourcecode:: xml

    <meiHead>
        <fileDesc>  <!-- required -->
            <titleStmt>  <!-- required -->
                <!-- NB: having all title parts in a containing <title>, and using the @type attribute,
                    are required for Lychee-MEI, and optional in standard MEI
                    NB: the @xml:lang and @translit are optional; their use will be specified later
                -->
                <title xml:lang="??" translit="?"> <!-- required -->
                    <title type="main"/>  <!-- required -->
                    <title type="subordinate"/>
                    <title type="abbreviated"/>
                    <title type="alternative"/>
                    <title type="translated"/>
                    <title type="uniform"/>
                </title>
                <!-- NB: the following <titleStmt> child elements are not required -->
                <respStmt>
                    <!-- this is for users who worked on the document -->
                    <!-- users may wish to credit Abjad; translatable string -->
                    <name type="process">Abjad API for Formalized Score Control</name>
                    <persName xml:id="p8109850029">
                        <!-- NB: use as many of the @type="full", @type="given", @type="other", and
                            @type="family" child elements as possible, according to what the person
                            responsible wishes
                            NB: the @xml:lang and @translit are optional, and will be specified later
                        -->
                        <persName type=""/>
                        <!-- if you want to include a link to the user's avatar -->
                        <ptr targettype="avatar" target="https://ncodacontent.org/p8109850029.jpg"/>
                    </persName>
                </respStmt>
                <!-- NB: the following are what is written on the engraved score; if they correspond
                    to a person in the <respStmt>, this should be done with a @nymref on the <persName>
                -->
                <arranger>
                    <!-- for an arranger who isn't a Lychee user -->
                    <persName xml:id="p12341234">
                        <persName type="full">Robert W. Smith</persName>
                    </persName>
                </arranger>
                <author>
                    <!-- for an author who is a Lychee user -->
                    <persName nymref="#p8109850029"/>
                </author>
                <composer><persName/></composer>
                <editor><persName/></editor>
                <funder><persName/></funder>
                <librettist><persName/></librettist>
                <lyricist><persName/></lyricist>
                <sponsor><persName/></sponsor>
            </titleStmt>

            <pubStmt>  <!-- required -->
                <!-- NB: all Lychee scores are considered unpublished for now -->
                <unpub>  <!-- required; text content is translatable -->
                    This is an unpublished Lychee-MEI document.
                </unpub>
            </pubStmt>
        </fileDesc>

        <workDesc>  <!-- (NB: not yet implemented) -->
            <work>
                <audience/>  <!-- e.g., "beginner bands" (NB: not yet implemented) -->
                <classification/>  <!-- like "keywords" (NB: not yet implemented) -->
                <contents/>  <!-- a description of doc contents (NB: not yet implemented) -->
                <context/>  <!-- socio-historical context (NB: not yet implemented) -->
                <history/>  <!-- (NB: not yet implemented) -->
                <key pname="" accid="" mode=""/>  <!-- (NB: not yet implemented) -->
                <langUsage/>  <!-- related to @xml:lang elsewhere (NB: not yet implemented) -->
                <mensuration/>  <!-- (NB: not yet implemented) -->
                <meter count="" sym="" unit=""/>  <!--  (NB: not yet implemented) -->
                <notesStmt/>  <!-- for score-wide notes left by users (NB: not yet implemented) -->
                <perfMedium/>  <!-- intened performers of this version (NB: not yet implemented) -->
            </work>
        </workDesc>

        <revisionDesc>
            <!-- NB: not implemented; will contain data from the Mercurial revlog -->
        </revisionDesc>
    </meiHead>

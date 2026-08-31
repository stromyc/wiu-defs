~CN WAUKESHA SUB — SWITCHED WIU SIGNAL FIELD ORDER
==================================================

PURPOSE
-------

This change corrects the signal naming/order for CN Waukesha Sub WIUs
containing one switch and three signal fields.

The raw WIU serialization order itself is not changing. The finding is
that the existing configuration assigned the NORMAL-route and
REVERSE-route signal names to the wrong ordinal fields at several
control points.

Multiple independent analyses, using separate capture sets and different
validation approaches, produced the same result:

    [SW][SIG1][SIG2][SIG3]
          |     |     |
          |     |     +---- REVERSE-route signal
          |     +---------- NORMAL-route signal
          +---------------- LONE point-side signal


=======================================================================
CN WAUKESHA SUB — SWITCHED WIU FIELD ORDER
=======================================================================

For a WIU containing one switch and three signals:

    [ SWITCH ][ SIGNAL 1 ][ SIGNAL 2 ][ SIGNAL 3 ]
       2 bits     5 bits     5 bits     5 bits

Physical roles:

    SIGNAL 1 = lone signal on point end
    SIGNAL 2 = normal-route signal on frog end
    SIGNAL 3 = reverse-route signal on frog end

Therefore:

    [SW][LONE][NORMAL][REVERSE]

This role ordering is invariant across the tested CN Waukesha Sub
control points.

Compass naming is NOT invariant and must be assigned by plant
orientation:

    lone N  -> paired heads SN / SR
    lone S  -> paired heads NN / NR


=======================================================================
PHYSICAL TURNOUT MODEL
=======================================================================

The important distinction is between the physical ROLE of a signal and
its compass NAME.

The field order remains:

    FIELD 0 = SWITCH
    FIELD 1 = LONE
    FIELD 2 = NORMAL
    FIELD 3 = REVERSE


Example: lone signal faces NORTH / WEST
--------------------------------

The point end is on the north/west side. The paired signals are on the
south/east frog end.

                                      NR
                                      |
                                  ----o--|
                                 /   SIG3
                                /    REVERSE
                               /     5 bits
                              /
                             /
NORTH / WEST       S       [SW]        NN             SOUTH / EAST
<===============o--|=======[]=========o--|===============>
                  SIG 1              SIG 2
                  LONE               NORMAL
                  5 bits             5 bits

                          
                          
Serialized field roles:

    [ SW ][  S  ][ NN ][ NR ]
      2      5      5     5      bits
             |      |     |
             |      |     +---- REVERSE
             |      +---------- NORMAL
             +----------------- LONE








Example: lone signal faces SOUTH
--------------------------------

The paired signals are on the north/west frog end. The lone signal is
on the south/east point end.

                   SR
                   |
                |--o--------
                 SIG3       \
                 REVERSE     \
                 5 bits       \
                               \
                                \
NORTH / WEST       SN               [SW]         N    SOUTH / EAST
<===============|--o==============[]==========o--|===============>
                  SIG2                         SIG1
                  NORMAL                       LONE
                  5 bits                      5 bits

              
Serialized field roles:

    [ SW ][  N  ][ SN ][ SR ]
      2      5      5     5      bits
             |      |     |
             |      |     +---- REVERSE
             |      +---------- NORMAL
             +----------------- LONE


=======================================================================
WHY SIG2 = NORMAL AND SIG3 = REVERSE
=======================================================================

The strongest discriminator is switch-position correlation. It does not
depend on the existing configuration names, ATCS mnemonics, milepost
names, or assumptions about train direction.

Across the tested switched plants:

    SWITCH = NORMAL

        SIG2 can display a governing/proceed aspect.
        SIG3 remains Stop.

    SWITCH = REVERSE

        SIG2 remains Stop.
        SIG3 can display a governing/proceed aspect.

This gives the complementary relationship:

                  SW=NORMAL       SW=REVERSE

    SIG2             PROCEED          STOP
    SIG3             STOP             PROCEED

Therefore:

    SIG2 = NORMAL-route signal
    SIG3 = REVERSE-route signal


SIG1 behaves differently.

SIG1 can govern movements with either switch position. When the switch
is Reverse, SIG1 can display a diverging-family aspect such as
Diverging Approach.

That behavior is expected because SIG1 is the single signal at the
point end of the turnout. It governs entry into the turnout regardless
of whether the route is lined Normal or Reverse.

Therefore:

    SIG1 = LONE point-side signal


=======================================================================
IMPORTANT CLASSIFIER FINDING
=======================================================================

An early validation heuristic incorrectly interpreted SIG1 becoming
more active under a Reverse switch lining as evidence that SIG1 might
be the reverse-route signal.

That interpretation was rejected.

A point-side signal can display a diverging-family aspect when the
turnout ahead is reversed. Therefore, "activity under Reverse" by
itself cannot identify the reverse-route head.

The correct discriminator is the complementary route gating:

    NORMAL-route head:

        proceeds under SW=N
        never proceeds under SW=R

    REVERSE-route head:

        never proceeds under SW=N
        proceeds under SW=R

    LONE point-side signal:

        can govern under SW=N
        can govern under SW=R
        may display diverging-family aspects under SW=R

Using this test produces:

    H1 = [SW][LONE][NORMAL][REVERSE]

with no tested plant supporting the competing SIG2/SIG3 ordering.


=======================================================================
INDEPENDENT VALIDATION
=======================================================================

The ordering was tested independently against multiple CN Waukesha Sub
capture sets.

The ThinkPad validation produced:

    H1 = 8
    H2 = 0
    H3 = 0

The result reproduced on a second independent capture:

    H1 = 8
    H2 = 0
    H3 = 0

At all eight testable plants:

    SIG2 proceeds only when the switch permits the NORMAL route.

    SIG3 proceeds only when the switch permits the REVERSE route.

No tested plant showed the opposite relationship.

Additional independent analysis on the Raspberry Pi capture reached the
same field-role ordering using a separate implementation and capture
window.

The independent analyses therefore converge on:

    [SW][SIG1][SIG2][SIG3]
         |     |     |
         |     |     +---- REVERSE
         |     +---------- NORMAL
         +---------------- LONE


=======================================================================
WHAT THIS FINDING DOES AND DOES NOT STANDARDIZE
=======================================================================

STANDARDIZED:

    FIELD 0 = SWITCH
    FIELD 1 = LONE
    FIELD 2 = NORMAL
    FIELD 3 = REVERSE

or:

    [SW][LONE][NORMAL][REVERSE]


NOT STANDARDIZED:

The compass direction represented by the LONE signal.

Depending on physical plant orientation:

    lone = N

        SIG1 = N
        SIG2 = SN
        SIG3 = SR

        [SW][N][SN][SR]


    lone = S

        SIG1 = S
        SIG2 = NN
        SIG3 = NR

        [SW][S][NN][NR]


Thus the universal rule concerns FIELD ROLE, not compass direction.


=======================================================================
REVIEW CONCLUSION
=======================================================================

The available raw capture evidence supports one universal field-role
ordering for CN Waukesha Sub one-switch/three-signal WIUs:

                  [SW][LONE][NORMAL][REVERSE]

or equivalently:

                  FIELD 0 = SWITCH
                  FIELD 1 = LONE
                  FIELD 2 = NORMAL
                  FIELD 3 = REVERSE

The Normal/Reverse determination comes directly from switch-conditioned
signal behavior and does not depend on the existing configuration
labels.

SIG2 and SIG3 exhibit complementary route gating:

    SIG2 -> NORMAL only
    SIG3 -> REVERSE only

SIG1 behaves as the common point-side signal and may govern either
lining.

The result was reproduced on independent capture sets and by separate
analysis efforts with no tested control point supporting the opposite
SIG2/SIG3 assignment.

Accordingly, swapping the existing Normal/Reverse labels on SIG2/SIG3
at the affected named control points is justified by the observed WIU
data.

Canonical rule for future CN Waukesha Sub switched-WIU definitions:

    [ SWITCH ][ LONE ][ NORMAL ][ REVERSE ]
       2 bits   5 bits   5 bits    5 bits~

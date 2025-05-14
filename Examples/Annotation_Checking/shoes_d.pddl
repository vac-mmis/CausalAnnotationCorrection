(define (domain shoes)
    (:requirements :negative-preconditions :typing :equality :disjunctive-preconditions)
    (:types location footwear)

	(:constants
    left_sock right_sock left_shoe right_shoe - footwear
    left_foot right_foot - location
  	)

    (:predicates
		(barefoot ?l - location) ; feet can wear nothing
		(hassock ?l - location) ; feet can wear socks
		(hasshoe ?l - location) ; feet can wear shoes
	)

  (:action putsock
	   :parameters (?o - footwear ?l - location)
	   :precondition (and
	                 (barefoot ?l)
	                 (not (hasshoe ?l))
	                 )
	   :effect       (when
	                    ;condition
	                    (or (and (= ?o left_sock) (=?l left_foot)) (and (= ?o right_sock) (=?l right_foot)))

	                    ;effect
	                    (and
	                    (not (barefoot ?l))
	                    (hassock ?l)
	                    )
	                )
	   )


    (:action putshoe
	   :parameters (?o - footwear ?l - location)
	   :precondition (hassock ?l)

	   :effect       (when
	                    ;condition
	                    (or (and (= ?o left_shoe) (=?l left_foot)) (and (= ?o right_shoe) (=?l right_foot)))

	                    ;effect
	                    (and
	                    (hasshoe ?l)
	                    (not (hassock ?l))
	                    )
	                 )

  )
)

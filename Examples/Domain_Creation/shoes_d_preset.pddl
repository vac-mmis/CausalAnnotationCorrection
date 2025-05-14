(define (domain shoes)
    (:requirements :negative-preconditions :typing)
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

	;insert your action definition


)

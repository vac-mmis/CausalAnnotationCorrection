(define (problem shoes-problem1)
(:domain shoes)

(:objects
    left_sock right_sock left_shoe right_shoe - object
    left_foot right_foot - location
  )

(:init
    (barefoot left_foot)
    (barefoot right_foot)

)

(:goal
    (and (hasshoe right_foot) (hasshoe left_foot))
)
)


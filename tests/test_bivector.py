import unittest
from math import isclose
from geometry_extension.bivector import face_bivector, face_area, face_normal


class FaceBivectorTests(unittest.TestCase):
    def test_triangle_2d(self):
        b = face_bivector([(0, 0), (2, 0), (0, 3)])
        self.assertEqual(b, ((0, 3), (-3, 0)))
        self.assertEqual(face_area([(0, 0), (2, 0), (0, 3)]), 3)

    def test_orientation_reverses(self):
        p = [(0, 0, 0), (2, 0, 0), (0, 3, 0)]
        a = face_bivector(p)
        b = face_bivector(list(reversed(p)))
        self.assertTrue(all(isclose(a[i][j], -b[i][j])
                            for i in range(3) for j in range(3)))
        self.assertEqual(face_normal(p), (0, 0, 1))

    def test_square_4d(self):
        p = [(0, 0, 0, 0), (2, 0, 0, 0),
             (2, 2, 0, 0), (0, 2, 0, 0)]
        self.assertEqual(face_area(p), 4)
        self.assertEqual(len(face_bivector(p)), 4)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            face_bivector([(0, 0), (1, 0)])
        with self.assertRaises(ValueError):
            face_bivector([(0, 0), (1, 0, 0), (0, 1)])
        with self.assertRaises(ValueError):
            face_normal([(0, 0, 0), (1, 0, 0), (2, 0, 0)])


if __name__ == "__main__":
    unittest.main()

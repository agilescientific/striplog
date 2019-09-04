# -*- coding: utf-8 -*-
"""
Define a suite a tests for the Striplog module.
"""
import numpy as np

from striplog.markov import Markov_chain


def test_basics():
    data = [[0, 37,  3,  2],
            [21,  0, 41, 14],
            [20, 25,  0,  0],
            [1, 14,  1,  0]]

    m = Markov_chain(data, states=['A', 'B', 'C', 'D'])

    assert str(m) == "Markov_chain(179 transitions, states=['A', 'B', 'C', 'D'], step=1)"

    ans = (35.73687369691601, 11.070497693516351, 0.9999989278539752)
    assert np.allclose(m.chi_squared(), ans)

    ans = np.array([[0., 31.27069125, 8.17143874, 2.55787001],
                    [31.28238248, 0., 34.05692583, 10.66069169],
                    [8.17137105, 34.04391563, 0., 2.78471333],
                    [2.5579797, 10.65716447, 2.78485582, 0.]])
    assert np.allclose(m.expected_counts, ans)


def test_sequence():
    data = "sssmmmlllmlmlsslsllsmmllllmssssllllssmmlllllssssssmmmmsmllllssslmslmsmmmslsllll"""
    m = Markov_chain.from_sequence(data, include_self=True)

    ans = np.array([[19., 5., 7.],
                    [6., 9., 5.],
                    [7., 6., 14.]])
    assert np.allclose(m.observed_counts, ans)

    ans = np.array([[0.49712747, 0.19796476, 0.30490777],
                    [0.49712747, 0.19796476, 0.30490777],
                    [0.49712747, 0.19796476, 0.30490777]])
    assert np.allclose(m.expected_freqs, ans)

    ans = np.array([[-2.24633883, -2.14054029, -2.81568096],
                    [-1.81677174,  1.82886491, -0.94412655],
                    [-2.68890472, -0.51627836,  0.76836845]])
    assert np.allclose(m.normalized_difference, ans)

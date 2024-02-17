import Polynomials as p;


def Roots(a,b,c):
    answerlist = []
    answerlist.append(p.quadraticPOS(a,b,c))
    answerlist.append(p.quadraticNEG(a,b,c))
    return answerlist


def Factorial(integertouse):
    return p.factorial(integertouse)

def Binomialterm(n,r):
    # N = (1+x)^n
    # R = term you want, eg X^r
    return p.terminexpansion(n,r)


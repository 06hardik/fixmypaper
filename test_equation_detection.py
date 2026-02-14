"""
Test the equation detection heuristic scoring system.
"""
from pdf_processor import PDFErrorDetector

# Create detector instance
detector = PDFErrorDetector()

# Test cases with expected results
test_cases = [
    # True equations
    ("E = mc²", True, "Classic Einstein equation"),
    ("F = ma     (1)", True, "Newton's second law with equation number"),
    ("x² + y² = r²", True, "Circle equation"),
    ("∑(i=1 to n) x_i = total", True, "Summation notation"),
    ("∫ f(x) dx = F(x) + C", True, "Integral equation"),
    ("a + b = c", True, "Simple algebraic equation"),
    ("y = mx + b     (2)", True, "Line equation with number"),
    ("λ = c/f", True, "Wavelength equation with Greek letter"),
    ("H(x) = -∑ p(x) log p(x)", True, "Entropy equation"),
    
    # False positives (should NOT be equations)
    ("The value of x = 5 in this example.", False, "Sentence with inline math"),
    ("(1) First, we need to understand the basics.", False, "Numbered list item"),
    ("This is the first step of the process.", False, "Regular sentence"),
    ("In the year 2020-2021, we conducted experiments.", False, "Date range"),
    ("The team members are John, Jane, and Bob.", False, "List of names"),
    ("According to the literature, this is important.", False, "Regular text"),
    ("(2) The second point is very critical.", False, "Another numbered list"),
    ("We can see that x = 10 and y = 20 in the data.", False, "Inline values"),
    
    # Edge cases
    ("x=5", True, "Compact equation without spaces"),
    ("Let x = 5", False, "Definition in text"),
    ("where a = coefficient", False, "Variable definition"),
    ("E=mc²     (3)", True, "Compact with equation number"),
]

print("=" * 80)
print("EQUATION DETECTION HEURISTIC TEST")
print("=" * 80)
print()

correct = 0
total = 0

for text, expected, description in test_cases:
    result = detector._is_likely_equation(text)
    status = "✓" if result == expected else "✗"
    
    # Calculate score for debugging
    score = 0
    line = text.strip()
    
    if re.search(r'[=+\-*/^×÷≤≥≈≠∑∫∂∇√∏∆λμπσΩαβγδεθ]', line):
        score += 2
    if re.search(r'\b[a-zA-Z]\b', line):
        score += 2
    if re.search(r'\(\d+\)\s*$', line):
        score += 5
    if not re.search(r'[.,;:]$', line):
        score += 1
    common_words = len(re.findall(r'\b(the|and|is|of|in|to|for|with|this|that|are|was|were|be|been|being|have|has|had|do|does|did|will|would|should|could|can|may|might)\b', line.lower()))
    if common_words > 2:
        score -= 3
    if re.match(r'^(The|This|That|These|Those|In|For|However|Therefore|Thus|Hence)\b', line):
        score -= 2
    if re.match(r'^\(\d+\)\s+[A-Z][a-z]+', line):
        score -= 4
    
    total += 1
    if result == expected:
        correct += 1
    
    print(f"{status} [{score:+3d}] {result!s:5} | Expected: {expected!s:5} | {description}")
    print(f"         Text: \"{text}\"")
    print()

print("=" * 80)
print(f"RESULTS: {correct}/{total} correct ({100*correct/total:.1f}%)")
print("=" * 80)

import re

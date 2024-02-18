teststring = "C152032: Opinion articles: head resorce includes property for checking opinion article; C155038: Verify Gameday Central in Sport section front; C171680: Verify the subnav How to Philly and Philly Best in section fronts; C152933: Verify that Scoreboard renders on liveblog with specific site sections; C167143: AMP Warning - Youtube video render with hidden class for AMP; C146654: Gallery Card in article body - data-card-type is added and has value \"gallery\"; C188164: Behavior of Account page when typing in a new account in Sign Up form and verify Sign up with Apple and Sign up with Google button"
tests = teststring.split(';')
for test in tests:
    newTestName = test.strip()
    newTestName = newTestName[0:7].strip()
    print(newTestName)
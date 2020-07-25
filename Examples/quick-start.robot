*** Settings ***
Library    PuppeteerLibrary
Test Teardown    Close Browser


*** Test Cases ***
Capture home screen page
    ${HEADLESS}     Get variable value    ${HEADLESS}    ${False}
    &{options} =    create dictionary   headless=${HEADLESS}
    Open browser    http://example.com  options=${options}
    Maximize Browser Window


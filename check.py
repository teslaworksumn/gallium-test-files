import sys
import os.path
import csv
import argparse
from collections import defaultdict

differences = defaultdict(dict)

def error(msg):
    print(f'ERROR: {msg}')
    sys.exit(1)

def compareFiles(truth, test):
    numCols = getNumberColumns(truth, test)
    numRows = getNumberOfRows(truth, test)

    with open(truth, 'r') as truthFile, open(test, 'r') as testFile:
        truthReader = csv.reader(truthFile)
        testReader = csv.reader(testFile)

        # go over CSV files at the same time and get the line number currently on
        # in lineNum
        for lineNum, (truthLine, testLine) in enumerate(zip(truthReader, testReader)):
            # there's a difference in the line
            if not truthLine == testLine:
                # go through the same line in both files value by value and get the
                # index of the current value in the line
                for channelNum, (truthVal, testVal) in enumerate(zip(truthLine, testLine)):
                    truthVal = int(truthVal)
                    testVal = int(testVal)
                    if not truthVal == testVal:
                        differences[lineNum][channelNum] = {
                            'computed': testVal,
                            'truth': truthVal,
                        }

    printSummary(differences, numCols, numRows)

def getNumberOfRows(truth, test):
    with open(truth, 'r') as truthFile, open(test, 'r') as testFile:
        truthNumRows = sum(1 for row in truthFile)
        testNumRows = sum(1 for row in testFile)

    if truthNumRows != testNumRows:
        error('Test file number of columns ({testNumRows}) does not match truth file number of columns ({truthNumRows})')

    # both files have the same number of rows so returning either is fine
    return truthNumRows


def getNumberColumns(truth, test):
    with open(truth, 'r') as truthFile, open(test, 'r') as testFile:
        truthReader = csv.reader(truthFile)
        testReader = csv.reader(testFile)

        truthNumCols = 0
        testNumCols = 0

        for line in truthReader:
            if not truthNumCols:
                truthNumCols = len(line)

            if truthNumCols != len(line):
                error('Truth file has inconsistent numbers of columns. Found {truthNumCols}, expected {len(line)}')

        for line in testReader:
            if not testNumCols:
                testNumCols = len(line)

            if testNumCols != len(line):
                error('Test file has inconsistent numbers of columns. Found {testNumCols}, expected {len(line)}')

    if truthNumCols != testNumCols:
        error('Test file number of columns ({testNumCols}) does not match truth file number of columns ({truthNumCols})')

    # both files have the same number of rows so returning either is fine
    return truthNumCols

def printSummary(differences, numRows, numCols):
    totalNumDifferences = 0

    for line, value in differences.items():
        numDifferences = len(value.items())
        totalNumDifferences += numDifferences
        print(f'Line {line:>4}: {numDifferences} differences(s)')

        for column, difference in value.items():
            print(f'  Actual: {difference["computed"]:>3} | Truth: {difference["truth"]:>3}')

    summaryText = 'Summary:'
    print(f'\n{summaryText}')
    print('-' * len(summaryText))

    rowsDifferent = len(differences)

    rowsDifferentText = f'{rowsDifferent}/{numRows} rows are different - {((numRows - rowsDifferent) / numRows) * 100:.2f}% match'
    totalNumValues = numRows * numCols
    valuesDifferentText = f'{totalNumDifferences}/{totalNumValues} values are different - {((totalNumValues - totalNumDifferences) / totalNumValues) * 100:.2f}% match'

    print(rowsDifferentText)
    print(valuesDifferentText)


def makeArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t', '--truth_file',
        help='Path to ground truth csv file',
        required=True,
    )

    parser.add_argument(
        '-e', '--test_file',
        help='Path to computed csv file to be tested against the ground truth value',
        required=True,
    )

    return parser

if __name__ == '__main__':
    args = makeArgParser().parse_args()

    if not os.path.isfile(args.truth_file):
        error(f'Truth file {args.truth_file} does not exist. Check path and try again.')
    if not os.path.isfile(args.test_file):
        error(f'Test file {args.test_file} does not exist. Check path and try again.')

    compareFiles(args.truth_file, args.test_file)

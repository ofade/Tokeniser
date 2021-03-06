# -*- coding: utf-8 -*-
import re

'''
Tokenisation rules are following:
- all punctuation marks are separated as tokens
- punctuation marks are not separated when we face double numbers, IP addresses, hyphenated names (eg Hewlett-Packard)
- for all possessive nouns/pronouns (that we identify with 's or s' we add (p) and remove the 's' as we don't want it to be a separate token as it doesn't carry much meaning
    examples of this would be: Jones\' -> Jones(p), Ivan's -> Ivan(p)
- we deal with negations (such as 'doesn't') by separating them into 2 tokens such as: does, not  (special case for can't as it needs to turn into cannot)
- identify acronyms such as U.K., U.S.A and so on and do not represent them as tokens
'''


class TokenisationController() :

    def __init__(self):
        ()

    def consecutive_characters_are_following_the_pattern(self, prev, current, regex_pattern):
        if  re.match(regex_pattern, current) and  re.match(regex_pattern, prev):
            return True
        return False

    def hypnen_needs_spaces_around(self, line, index) :
        alphanumericalCharacters = r'[a-zA-Z0-9]'
        return (not re.search(alphanumericalCharacters, line[index - 1]) and not re.search(alphanumericalCharacters,line[index + 1])) \
               or (not re.search(alphanumericalCharacters, line[index-1]) and re.search(alphanumericalCharacters,line[index + 1])) \
                or ( re.search(alphanumericalCharacters, line[index-1]) and not re.search(alphanumericalCharacters,line[index + 1]))

    def insert_identifier_at_index(self, identifer, index, line, spaceAfterIdentifier) :
        if spaceAfterIdentifier :
            return line[:index] + identifer + " " + line[index+len(identifer):]
        return line[:index] + identifer + line[index + len(identifer):]


    def insert_space_after_item_at_some_index(self, line, index) :
        return line[:index+1] + " " + line[index+1:]

    def insert_space_before_item_at_some_index(self, line, index) :
        return line [:index]+ " " + line[index:]

    def is_given_char_apostrophe_followed_by_lowercase_chars(self, item, line, currentItemsIndex):
        lowerCaseLetters = r'[a-z]'
        apostrophe = r'[\']'
        return (re.search(apostrophe, item)) and re.search(lowerCaseLetters, line[currentItemsIndex - 1])

    def is_item_surrounded_by_specified_characters(self, letterOne, letterTwo, line, currentItemIndex) :
        return re.search(letterOne, line[currentItemIndex - 1]) and re.search(letterTwo, line[currentItemIndex + 1])

    def deal_with_possessive_nouns(self, item, line, index, modificationsMade, lineCopy) :
        # dealing with possessive nouns in plural
        if re.search('\'', item) and re.search('s', line[index - 1]):
            lineCopy = self.insert_identifier_at_index('(p)', index + modificationsMade, lineCopy, True)
            modificationsMade = modificationsMade + 1

        # dealing with possessive nouns in singular
        if self.is_given_char_apostrophe_followed_by_lowercase_chars(item, line, index):
            if (index + 1 <= len(line) - 1):
                if re.search(' ', line[index + 1]) or re.search('s', line[index + 1]):
                    lineCopy = self.insert_identifier_at_index('(p)', index + modificationsMade, lineCopy, True)
                    modificationsMade = modificationsMade + 1
        return lineCopy

    def deal_with_apostrophe(self, index, modificationsMade, lineCopy) :
        lineCopy = self.insert_space_after_item_at_some_index(lineCopy, index + modificationsMade)
        lineCopy = self.insert_space_after_item_at_some_index(lineCopy, index - 1 + modificationsMade)
        return lineCopy

    def is_item_surrounded_by_matching_characters(self, index, line, regularExpressionForCharacterMatch):
        if index+1 != len(line) :
            return re.search(regularExpressionForCharacterMatch, line[index-1]) and re.search(regularExpressionForCharacterMatch, line[index+1])
        return re.search(regularExpressionForCharacterMatch, line[index - 1])

    def remove_space_at_index(self, index, line):
        return line[:index-1] + line[index:]


    def deal_with_negations(self, item, line, index, modificationsMade, lineCopy) :
        lineCopy = self.insert_space_after_item_at_some_index(lineCopy, index - 2 + modificationsMade)
        modificationsMade = modificationsMade + 1
        lineCopy = self.insert_identifier_at_index('o', index + modificationsMade, lineCopy, False)
        return lineCopy

    def tokenise(self, line) :
        #regular expressions
        specialSymbols = r'[?,!():;$£%^&*¬+]'
        alphanumericalCharacters= r'[a-zA-Z0-9]'
        capitalLetters = r'[A-Z]'
        hyphen = r'[-]'
        dot = r'[.]'
        alphaCharacters = r'[a-zA-Z]'

        modificationsMade = 0 #for indexing reasons
        lineCopy = line #copy of the original piece of text, needed for indexing reasons
        for index,item in enumerate(line):
            prev = line[index - 1]
            lineCopyIndex = index + modificationsMade
            if index != 0: #cases where need to check the previous symbol before the actual item we're looking at

                lineCopy = self.deal_with_possessive_nouns(item, line, index, modificationsMade, lineCopy)

                #dealing with negations like "don't", "doesn't"
                if self.is_given_char_apostrophe_followed_by_lowercase_chars(item, line, index) and self.is_item_surrounded_by_specified_characters('n', 't', line, index):
                    if line[index-3:index] == 'can' : #deal with can't -> cannot
                        lineCopy = lineCopy[:index] + 'not' + lineCopy[index+2:]
                    else:
                         lineCopy = self.deal_with_negations(item, line, index, modificationsMade, lineCopy)

                # deal with last names and other cases where pattern is like [A-Z'A-Z]
                if re.search('\'', item) and index != len(line) -1 :
                    if re.search(capitalLetters, prev) and re.search(capitalLetters, line[index+1]) :
                        lineCopy = self.deal_with_apostrophe(index, modificationsMade, lineCopy)

                # dealing with hyphens (e.g. up-to-date - in this case there should be no changes)
                if (re.search(hyphen, item)):
                    if index + 1 < len(line) and self.hypnen_needs_spaces_around(line, index):
                        lineCopy = self.insert_space_after_item_at_some_index(lineCopy, lineCopyIndex)
                        lineCopy = self.insert_space_before_item_at_some_index(lineCopy, lineCopyIndex)


            #cater for cases when there are dots that are not surrounded by alphanumerical characters and that need to be separated
            if re.search(dot, item) and not self.is_item_surrounded_by_matching_characters(index, line, alphanumericalCharacters) :
                lineCopy = self.insert_space_after_item_at_some_index(lineCopy, lineCopyIndex)

            #cater for acronyms - if we detect that we're looking at the acronym, then we remove a space that was previously added
            if re.search(dot, item) and self.is_item_surrounded_by_matching_characters(index, line, capitalLetters):
                lineCopy = self.remove_space_at_index(lineCopyIndex, lineCopy)

            #separate punctuation but don't separate digits if there's punctuation between them
            if re.search(specialSymbols,item) and  not self.consecutive_characters_are_following_the_pattern(prev, item, r'\d') :
                lineCopy = self.insert_space_after_item_at_some_index(lineCopy, lineCopyIndex)


            if re.search(alphaCharacters, item) and index != len(line) - 1:
                if re.search(specialSymbols, line[index+1]) or re.search(dot, line[index+1]): #if the next symbol after the letter letter is a special symbol
                    lineCopy = self.insert_space_after_item_at_some_index(lineCopy, lineCopyIndex)

            modificationsMade = len(lineCopy) - len(line)

        return lineCopy.split()
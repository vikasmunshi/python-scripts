#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

########################################################################################################################
#    MIT License                                                                                                       #
#                                                                                                                      #
#    Copyright (c) 2018 Vikas Munshi <vikas.munshi@gmail.com>                                                          #
#                                                                                                                      #
#    Permission is hereby granted, free of charge, to any person obtaining a copy                                      #
#    of this software and associated documentation files (the "Software"), to deal                                     #
#    in the Software without restriction, including without limitation the rights                                      #
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell                                         #
#    copies of the Software, and to permit persons to whom the Software is                                             #
#    furnished to do so, subject to the following conditions:                                                          #
#                                                                                                                      #
#    The above copyright notice and this permission notice shall be included in all                                    #
#    copies or substantial portions of the Software.                                                                   #
#                                                                                                                      #
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR                                        #
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,                                          #
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE                                       #
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER                                            #
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,                                     #
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE                                     #
#    SOFTWARE.                                                                                                         #
########################################################################################################################

from os.path import expanduser

from . import Agent, Custodians, Secret, Shares

if __name__ == '__main__':
    uuid = 'test-abcd-efgh'
    custodians1 = Custodians('./vault/custodians.json')
    agent1 = Agent(name='agent x', private_key=expanduser('~/.ssh/id_rsa'))
    s1 = Secret(secret='abcdefgh', custodians=custodians1, agent=agent1, uuid=uuid)
    custodians1.send_shares()

    custodians2 = Custodians('./vault/custodians.json')
    agent2 = Agent(name='agent y')
    custodians2.request_shares(agent=eval(repr(agent2)), uuid=uuid)
    custodians2.receive_shares(agent=eval(repr(agent2)), uuid=uuid)
    shares = Shares([custodian.share for custodian in custodians2])
    s2 = Secret(shares=shares, agent=agent2)

    print(s1.apply(func=lambda s: s) == s2.apply(func=lambda s: s))



# Copyright (c) 2024 Rushikesh Sunil Kotkar.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

class TreeNode:
    def __init__(self, val):
        self.key = val
        self.left = None
        self.right = None


class orderdmultiset:
    def __init__(self):
        """
        Created a node for balanced binary search and a list to store all elements in it
        """
        ##Created By Rushikesh Sunil Kotkar
        self.root = None
        self.multiset = []

    def insert(self, node, key):
        """
        Inserted an element in O(log n) times
        """
        ##Created By Rushikesh Sunil Kotkar
        if node is None:
            return TreeNode(key)
        elif key < node.key:
            node.left = self.insert(node.left, key)
        else:
            node.right = self.insert(node.right, key)
            ##Created By Rushikesh Sunil Kotkar
        node = self.balfact(node)
        return node

    def erase(self, key):
        self.root = self.deleteele(self.root, key)
        l=len(self.multiset)
        self.multiset = []
        ##Created By Rushikesh Sunil Kotkar
        self.inorder(self.root, self.multiset)
        return l>len(self.multiset)

    def deleteele(self, node, key):
        """
        To delete an element in O(log n) Times
        """
        if node is None:
            return node
        elif key < node.key:
            node.left = self.deleteele(node.left, key)
        elif key > node.key:
            ##Created By Rushikesh Sunil Kotkar
            node.right = self.deleteele(node.right, key)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                successor = self.minnode(node.right)
                node.key = successor.key
                ##Created By Rushikesh Sunil Kotkar
                node.right = self.deleteele(node.right, successor.key)
        node = self.balfact(node)
        return node

    def search(self, element):
        return self.searchele(self.root, element)

    def searchele(self, node, element):
        """
                To Search an element in O(log n) Times
                """
        if node is None or node.key == element:
            return node
        if element < node.key:
            ##Created By Rushikesh Sunil Kotkar
            return self.searchele(node.left, element)
        return self.searchele(node.right, element)

    def append(self, element):
        self.root = self.insert(self.root, element)
        self.multiset = []
        ##Created By Rushikesh Sunil Kotkar
        self.inorder(self.root, self.multiset)
        return self.multiset

    def inorder(self, node, result):
        """
                To Show elements in O(log n) Times
                """
        if node:
            self.inorder(node.left, result)
            result.append(node.key)
            ##Created By Rushikesh Sunil Kotkar
            self.inorder(node.right, result)

    def height(self, node):
        if node is None:
            return 0
        ##Created By Rushikesh Sunil Kotkar
        return 1 + max(self.height(node.left), self.height(node.right))

    def calcbalancefac(self, node):
        if node is None:
            ##Created By Rushikesh Sunil Kotkar
            return 0
        return self.height(node.left) - self.height(node.right)

    def leftro(self, node):
        rgh = node.right
        ##Created By Rushikesh Sunil Kotkar
        t = rgh.left

        rgh.left = node
        node.right = t

        return rgh

    def rightro(self, node):
        lft = node.left
        ##Created By Rushikesh Sunil Kotkar
        t = lft.right

        lft.right = node
        node.left = t

        return lft

    def balfact(self, node):
        if node is None:
            ##Created By Rushikesh Sunil Kotkar
            return node

        bal = self.calcbalancefac(node)

        if bal > 1:
            if self.calcbalancefac(node.left) < 0:
                ##Created By Rushikesh Sunil Kotkar
                node.left = self.leftro(node.left)
            return self.rightro(node)
        if bal < -1:
            if self.calcbalancefac(node.right) > 0:
                ##Created By Rushikesh Sunil Kotkar
                node.right = self.rightro(node.right)
            return self.leftro(node)
        return node
    def minnode(self, node):
        curr = node
        ##Created By Rushikesh Sunil Kotkar
        while curr.left:
            curr = curr.left
        return curr


"""
-Functions :-->
    var_name=o()--->To create an object of sorted multiset
    var_name.append(element:int)---> To add an element in  O(log n)
    var_name.search(element:int)--->To search an element in O(log n)
    var_name.erase(element:int)--->To delete an element in O(log n)
-To access all the stored elements u can use following syntax:-->
    var_name.multiset---> A list where all the element are stored
"""
# ml = o()
# ml.append(10)
# ml.append(20)
# ml.append(30)
#
# ml.append(40)
# ml.append(50)
#
# print(ml.multiset)
# print(ml.multiset)

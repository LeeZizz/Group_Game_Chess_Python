import pygame


class GameState():
    def __init__(self):
        # Bảng quân cờ, chữ cái đầu là màu quân cờ: b(black) ,w(white)
        # Chữ cái thứ 2 là tên quân cờ: R(rook), N(knight), B(bishop), Q(queen), K(king), p(pawn)
        # Bàn cờ 8x8 với ma trận 2 chiều
        # '--' là chỗ trống để các quân di chuyển
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]

        # self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
        #                       'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True  # cho biết là lượt của quân trắng hay quân đen
        self.moveLog = []  # Nhật ký bàn cờ ghi lại các nước cờ di chuyển
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        # self.pins=[]
        self.enpassantPossible = ()  # Tọa độ ô vuông khi "en passant" là hợp lệ
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMoved(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # Ghi lại các nước cờ
        self.whiteToMove = not self.whiteToMove  # Chuyển người chơi
        # Cập nhật vị trí King
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Phong cấp tốt
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # Ăn tốt qua đường
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # Bắt tốt

        # Cập nhật vị trí nước đi tốt qua đường
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # chỉ khi đi 2 bước
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # Nhập thành
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # nhập thành bên vua
                # Di chuyển xe
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:  # nhập thành bên hậu
                # Di chuyển xe
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'
        self.enpassantPossibleLog.append(self.enpassantPossible)

        # Cập nhật quyền nhập thành
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMoved(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # Cập nhật vị trí King
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # Undo ăn tốt qua đường
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            # Undo quyền nhập thành
            self.castleRightsLog.pop()  # Loại bỏ quyền nhập thành từ nước vừa đi
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs,
                                                     newRights.bqs)  # Đặt quyền nhập thành hiện tại trở lại nước cũ
            # Undo nhập thành
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # nhập thành bên vua
                    # Di chuyển xe
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # nhập thành bên hậu
                    # Di chuyển xe
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'
            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # Xe trái
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # Xe phải
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # Xe trái
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # Xe phải
                    self.currentCastlingRight.bks = False
        # Nếu xe bị bắt rồi
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # Tạo tất cả nước đi:
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCatleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCatleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # Thực hiện các nước đi
        for i in range(len(moves) - 1, -1, -1):
            self.makeMoved(moves[i])
            # Khi makeMoved() sẽ chuyển turn sang người chơi khác
            # Nên cần phải chuyển turn lại để thực hiện với đúng quân cần kiểm tra
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # Nếu chúng tấn công King, nó không phải là nước đi hợp lệ
                moves.remove(moves[i])
            # Khi undoMoved() cũng sẽ chuyển turn sang người chơi khác
            # Tương tự makeMoved()
            self.whiteToMove = not self.whiteToMove
            self.undoMoved()
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    # Kiểm tra xem có bị chiếu tướng không?
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # Kiểm tra xem địch có thể tấn công ô (r, c) không?
    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove
        oopMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oopMoves:
            if move.endRow == row and move.endCol == col:  # Ô bị tấn công
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        # duyệt các ô vuông trên bàn cờ
        for row in range(8):
            for col in range(8):
                colorPiece = self.board[row][col][0]
                if (colorPiece == 'w' and self.whiteToMove) or (colorPiece == 'b' and self.whiteToMove == False):
                    piece = self.board[row][col][1]
                    if piece == 'p':  # là quân tốt
                        self.getPawnMoves(row, col, moves)
                    elif piece == 'N':  # là quân mã
                        self.getKnightMoves(row, col, moves)
                    elif piece == 'B':  # là quân tượng
                        self.getBishopMoves(row, col, moves)
                    elif piece == 'R':  # là quân xe
                        self.getRookMoves(row, col, moves)
                    elif piece == 'Q':  # là quân hậu
                        self.getQueenMoves(row, col, moves)
                    elif piece == 'K':  # là quân vua
                        self.getKingMoves(row, col, moves)

        return moves




    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove and row-1>=0:  # Tốt trắng di chuyển
            if self.board[row - 1][col] == '--':  # 1 ô phía trước trống?
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == '--':  # 2 ô phía trước trống?
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:  # Tốt bắt trái
                if self.board[row - 1][col - 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col - 1), self.board, isEnpassantMove=True))
            if col + 1 <= 7:  # Tốt bắt phải
                if self.board[row - 1][col + 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, isEnpassantMove=True))
        elif self.whiteToMove == False and row+1<=7:  # Tốt đen di chuyển
            if self.board[row + 1][col] == '--':  # 1 ô phía trước trống?
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == '--':  # 2 ô phía trước trống?
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:  # Tốt bắt trái
                if self.board[row + 1][col - 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, isEnpassantMove=True))
            if col + 1 <= 7:  # Tốt bắt phải
                if self.board[row + 1][col + 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row + 1, col+ 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Lên, trái, xuống, phải
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Trên bàn cờ
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # Ô trống được đi
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Ăn quân địch
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # Quân mình thì bị chặn không đi được
                        break
                else:  # Ngoài bàn cờ
                    break

    def getKnightMoves(self, r, c, moves):
        directions = ((-2, -1), (-2, 1), (-1, -2), (1, -2), (2, -1), (2, 1), (-1, 2), (1, 2))
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Trên bàn cờ
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Ô trống hoặc quân địch
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Trên bàn cờ
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # Ô trống được đi
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Ăn quân địch
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # Quân mình thì bị chặn không đi được
                        break
                else:  # Ngoài bàn cờ
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + directions[i][0]
            endCol = c + directions[i][1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Trên bàn cờ
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Ô trống hoặc quân địch
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    # Tạo toàn bộ nước đi nhập thành cho vua tại (r, c) và thêm vào danh sách nước đi
    def getCatleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  # Khi bị chiếu thì không nhập thành được
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks #white king side
        self.bks = bks #black king side
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Phong cấp tốt
        self.isPawnPromotion = (
                (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7))
        # Ăn tốt qua đường
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # Nhập thành
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __str__(self):

        #castle move
        if self.isCastleMove:
            return  "O-O" if self.endCol == 6 else "O-O-O"
            #"O-O" #king side castlse
            #"O-O-O" # queen side castle
        endSquare = self.getRankFile(self.endRow, self.endCol)
        # pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol]+'x'+endSquare
            else:return endSquare
            #pawn promotions
        #2 quân cờ cùng loại di chuyển đến 1 ô vuông, Nbd2 nếu 2 quân mã có thể di chuyển tới d2
        #sau đó thêm + cho checkmove, và # cho chiếu chiếu hết
        #piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += 'x'
        return moveString + endSquare
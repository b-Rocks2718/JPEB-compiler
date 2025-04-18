module AsmGen where

import TypedAST(SymbolTable, IdentAttrs(..), Const_ (getConstInt), Type_ (ArrayType))
import qualified TACAST
import AsmAST
import Utils
import ParserUtils (typeSize)

progToAsm :: TACAST.Prog -> SymbolTable -> (Prog, [(String, Operand)])
progToAsm (TACAST.Prog p) symbols =
  let rslt = topLevelToAsm symbols <$> p
  in (Prog (fst <$> rslt), concatMap snd rslt)

topLevelToAsm :: SymbolTable -> TACAST.TopLevel -> (TopLevel, [(String, Operand)])
topLevelToAsm symbols (TACAST.Func name global params body) =
  (Func name global $ replacePseudo maps <$> instrs, maps)
  where (maps, size) = createMaps instrs symbols
        instrs = AllocateStack (size + 1)  : paramsToAsm params ++ (body >>= exprToAsm)
topLevelToAsm _ (TACAST.StaticVar name global _ init_) = (StaticVar name global init_, [])
topLevelToAsm _ (TACAST.Comment s) = (Comment s, [])

paramsToAsm :: [String] -> [Instr]
paramsToAsm ps = getZipList (ZipList copyList <*> ZipList ps)
  where copyList =
          [\s -> Mov (Pseudo s) (Reg R3),
           \s -> Mov (Pseudo s) (Reg R4),
           \s -> Mov (Pseudo s) (Reg R5),
           \s -> Mov (Pseudo s) (Reg R6)] ++
           ((\n s -> Mov (Pseudo s) (Memory bp n)) <$> [2..])

exprToAsm :: TACAST.Instr -> [Instr]
exprToAsm instr =
  case instr of
    (TACAST.Return val) -> [Mov (Reg R3) (tacValToAsm val), Ret]
    (TACAST.Copy dst src) -> [Mov (tacValToAsm dst) (tacValToAsm src)]
    (TACAST.Unary op dst src) ->
      [Unary op (tacValToAsm dst) (tacValToAsm src)]
    (TACAST.Binary op dst src1 src2 type_) ->
      [Binary op (tacValToAsm dst) (tacValToAsm src1) (tacValToAsm src2) type_]
    (TACAST.CondJump cond label) -> [CondJump cond label]
    (TACAST.Cmp val1 val2) -> [Cmp (tacValToAsm val1) (tacValToAsm val2)]
    (TACAST.Jump label) -> [Jump label]
    (TACAST.Label s) -> [Label s]
    (TACAST.Call name dst srcs) ->
      -- push in reverse order
      getZipList (ZipList stackList <*> ZipList (reverse stackArgs)) ++
      getZipList (ZipList regList <*> ZipList regArgs) ++
      [Call name,
      AllocateStack (length stackArgs), -- deallocate stack
      Mov (tacValToAsm dst) (Reg R3)]
      where regList =
              [Mov (Reg R3) . tacValToAsm,
               Mov (Reg R4) . tacValToAsm,
               Mov (Reg R5) . tacValToAsm,
               Mov (Reg R6) . tacValToAsm]
            regArgs = take 4 srcs
            stackArgs = drop 4 srcs
            stackList = repeat (Push . tacValToAsm)
    (TACAST.GetAddress dst src) -> [GetAddress (tacValToAsm dst) (tacValToAsm src)]
    (TACAST.Load dst ptr) -> [Mov (Reg R3) (tacValToAsm ptr),
                              Mov (Reg R4) (Memory R3 0),
                              Mov (tacValToAsm dst) (Reg R4)]
    (TACAST.Store ptr src) -> [Mov (Reg R3) (tacValToAsm ptr),
                               Mov (Reg R4) (tacValToAsm src),
                              Mov (Memory R3 0) (Reg R4)]
    (TACAST.CopyToOffset dst src offset) -> [Mov (makePseudoMem dst offset) (tacValToAsm src)]

createMaps :: [Instr] -> SymbolTable -> ([(String, Operand)], Int)
createMaps xs symbols = foldr (createMapsFold symbols) ([], -1) (reverse (xs >>= getOps))

createMapsFold :: SymbolTable -> Operand -> ([(String, Operand)], Int) -> ([(String, Operand)], Int)
createMapsFold symbols opr (maps, size) =
  case opr of
    (Pseudo v) ->
      case lookup v maps of
        (Just _) -> (maps, size)
        Nothing -> case lookup v symbols of
          -- static var is stored in data section, not stack
          Just (_, StaticAttr _ _) -> ((v, Data v):maps, size)
          _ -> ((v, Memory bp size):maps, size - 1)
    (PseudoMem v _) ->
      case lookup v maps of
        (Just _) -> (maps, size)
        Nothing -> do
          case lookup v symbols of
          -- static var is stored in data section, not stack
            Just (_, StaticAttr _ _) -> ((v, Data v):maps, size)
            Just (type_@(ArrayType _ _), LocalAttr) -> do
              (replace v (Memory bp (size - typeSize type_ + 1)) maps, size - typeSize type_)
            _ -> error "Compiler Error: this shouldn't happen" -- ((v, Memory bp size):maps, size - 1)
    _ -> (maps, size)

getOps :: Instr -> [Operand]
getOps x = getDst x ++ getSrcs x

getSrcs :: Instr -> [Operand]
getSrcs x =
  case x of
    Mov _ b -> [b]
    Unary _ _ b -> [b]
    Binary _ _ b c _ -> [b, c]
    Cmp a b -> [a, b]
    Push a -> [a]
    GetAddress _ b -> [b]
    _ -> []

getDst :: Instr -> [Operand]
getDst x =
  case x of
    Mov a _ -> [a]
    Unary _ a _ -> [a]
    Binary _ a _ _ _ -> [a]
    GetAddress a _ -> [a]
    _ -> []

-- map identifiers used as src/dst to stack locations
replacePseudo :: [(String, Operand)] -> Instr -> Instr
replacePseudo maps = mapOps f
  where f (Pseudo v) = case lookup v maps of
          (Just newOp) -> newOp
          Nothing -> error "Compiler Error: Missing map for pseudoregister"
        f (PseudoMem v offset) = case lookup v maps of
          (Just (Memory base a)) -> Memory base (a + offset)
          _ -> error "Compiler Error: Missing map for pseudomem"
        f op = op

mapOps :: (Operand -> Operand) -> Instr -> Instr
mapOps f (Mov a b) = Mov (f a) (f b)
mapOps f (Unary op a b) = Unary op (f a) (f b)
mapOps f (Binary op a b c type_) = Binary op (f a) (f b) (f c) type_
mapOps f (Cmp a b) = Cmp (f a) (f b)
mapOps f (Push a) = Push (f a)
mapOps f (GetAddress a b) = GetAddress (f a) (f b)
mapOps _ x = x

tacValToAsm :: TACAST.Val -> Operand
tacValToAsm (TACAST.Constant n) = Lit $ getConstInt n
tacValToAsm (TACAST.Var s) = Pseudo s
tacValToAsm (TACAST.Arr s _) = PseudoMem s 0

makePseudoMem :: TACAST.Val -> Int -> Operand
makePseudoMem (TACAST.Arr s _) = PseudoMem s
makePseudoMem x = error $ "Compiler Error: attempted to make PseudoMem for non-var " ++ show x
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

class Node {
  public boolean n;
  public boolean s;
  public boolean e;
  public boolean w;
  public boolean nw;
  public boolean ne;
  public boolean sw;
  public boolean se;

  public Node() {
    n = true;
    s = true;
    e = true;
    w = true;
    nw = true;
    sw = true;
    ne = true;
    se = true;
  }

  public Node(Node nod) {
    this.n = nod.n;
    this.s = nod.s;
    this.e = nod.e;
    this.w = nod.w;
    this.nw = nod.nw;
    this.ne = nod.ne;
    this.sw = nod.sw;
    this.se = nod.se;
  }

  public boolean isValid(String str) {
    if (str.equals("north")) return n;
    else if (str.equals("south")) return s;
    else if (str.equals("east")) return e;
    else if (str.equals("west")) return w;
    else if (str.equals("northwest")) return nw;
    else if (str.equals("southwest")) return sw;
    else if (str.equals("northeast")) return ne;
    else return se;
  }

}

class Coords {
  public int row;
  public int col;
  public Coords(int row, int col) {
    this.row = row;
    this.col = col;
  }
}

public class Client {
  public static Node[][] board = new Node[15][15];
  static int row = 5;
  static int col = 5;
  static int goalRow = -111;
  static int player = 0;
  static String bestMove = "";
  static int playerNum = 0;

  private final Random randomGenerator;
  protected String host;
  protected int port;
  protected List<String> actions = new ArrayList<String>();
  protected String name = "American-Emigrants";

  public Client(String host, int port) {
    this.host = host;
    this.port = port;
    initialize_actions();
    randomGenerator = new Random();
  }

  private void initialize_actions() {
    actions.add("north west");
    actions.add("north");
    actions.add("north east");
    actions.add("east");
    actions.add("south east");
    actions.add("south");
    actions.add("south west");
    actions.add("west");
  }

  public static void main(String[] args) {
    Client c = new Client("localhost", 8023);
    try {
      c.play_game();
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  private void initBoard() {
    for (int i = 0; i < board.length; i++) {
      for (int j = 0; j < board.length; j++) {
        board[i][j] = new Node();
        board[i][j].nw = (i == 0)  || (j == 0)                  ? false : true;
        board[i][j].n  = (i == 0)  || (j == 0) || (j == 14)   ? false : true;
        board[i][j].ne = (i == 0)  || (j == 14)                 ? false : true;
        board[i][j].w  = (j == 0)  || (i == 0) || (i == 14)   ? false : true;
        board[i][j].e  = (j == 14) || (i == 0) || (i == 14)   ? false : true;
        board[i][j].sw = (i == 14) || (j == 0)                  ? false : true;
        board[i][j].s  = (i == 14) || (j == 0) || (j == 14)   ? false : true;
        board[i][j].se = (i == 14) || (j == 14)                 ? false : true;
      }
    }

    board[0][6].ne = true;
    board[0][7].nw = true;
    board[0][7].n  = true;
    board[0][7].ne = true;
    board[0][8].nw = true;
    board[14][6].se = true;
    board[14][7].sw = true;
    board[14][7].s  = true;
    board[14][7].se = true;
    board[14][8].sw = true;
  }

  private Coords updateBoard(Node[][] b, String move, int lrow, int lcol, boolean isGlobal) {
    if (!isGlobal) {
      try{
        if (move.equals("north west")) {
          if (b[lrow][lcol].nw == false);
          b[lrow][lcol].nw = false;
          lrow --;
          lcol --;
          b[lrow][lcol].se = false;
        } else if (move.equals("north")) {
          if (b[lrow][lcol].n == false);
          b[lrow][lcol].n = false;
          lrow --;
          b[lrow][lcol].s = false;
        } else if (move.equals("north east")) {
          if (b[lrow][lcol].ne == false);
          b[lrow][lcol].ne = false;
          lrow --;
          lcol ++;
          b[lrow][lcol].sw = false;
        } else if (move.equals("west")) {
          if (b[lrow][lcol].w == false);
          b[lrow][lcol].w = false;
          lcol --;
          b[lrow][lcol].e = false;
        } else if (move.equals("east")) {
          if (b[lrow][lcol].e == false);
          b[lrow][lcol].e = false;
          lcol ++;
          b[lrow][lcol].w = false;
        } else if (move.equals("south west")) {
          if (b[lrow][lcol].sw == false);
          b[lrow][lcol].sw = false;
          lrow ++;
          lcol --;
          b[lrow][lcol].ne = false;
        } else if (move.equals("south")) {
          if (b[lrow][lcol].s == false);
          b[lrow][lcol].s = false;
          lrow ++;
          b[lrow][lcol].n = false;
        } else if (move.equals("south east")) {
          if (b[lrow][lcol].se == false);
          b[lrow][lcol].se = false;
          lrow ++;
          lcol ++;
          b[lrow][lcol].nw = false;
        }
      } catch (Exception e){
        System.out.println("goggaoidjgaogsdoal");
        //goal case, we don't give a fuck
        Coords newCoords = new Coords(-999, -999);
        return newCoords;
      }

      Coords newCoords = new Coords(lrow, lcol);
      return newCoords;
    } else {
      if(move.contains("north west")){move = "north west";}
      else if(move.contains("north east")){move = "north east";}
      else if(move.contains("south west")){move = "south west";}
      else if(move.contains("south east")){move = "south east";}
      else if(move.contains("north") ){move = "north"; }
      else if(move.contains("west") ){move = "west";}
      else if(move.contains("east") ){move = "east";}
      else if(move.contains("south") ){move =  "south";}

      try{
        if (move.equals("north west")) {
          if (board[row][col].nw == false);
          board[row][col].nw = false;
          row --;
          col --;
          board[row][col].se = false;
        } else if (move.equals("north")) {
          if (board[row][col].n == false);
          board[row][col].n = false;
          row --;
          board[row][col].s = false;
        } else if (move.equals("north east")) {
          if (board[row][col].ne == false);
          board[row][col].ne = false;
          row --;
          col ++;
          board[row][col].sw = false;
        } else if (move.equals("west")) {
          if (board[row][col].w == false);
          board[row][col].w = false;
          col --;
          board[row][col].e = false;
        } else if (move.equals("east")) {
          if (board[row][col].e == false);
          board[row][col].e = false;
          col ++;
          board[row][col].w = false;
        } else if (move.equals("south west")) {
          if (board[row][col].sw == false);
          board[row][col].sw = false;
          row ++;
          col --;
          board[row][col].ne = false;
        } else if (move.equals("south")) {
          if (board[row][col].s == false);
          board[row][col].s = false;
          row ++;
          board[row][col].n = false;
        } else if (move.equals("south east")) {
          if (board[row][col].se == false);
          board[row][col].se = false;
          row ++;
          col ++;
          board[row][col].nw = false;
        }
      } catch (Exception e){
        System.out.println("goggaoidjgaogsdoal");
        //goal case, we don't give a fuck
      }
      return null;
    }
  }

  private int distToGoal(int lrow, int lcol, int lplayer) {
    if (lplayer == player) {
      return Math.abs(goalRow - lrow);
    } else {
      return Math.abs((15-goalRow) - lrow);
    }
  }

  private void printBoard(Node[][] boa){
    String a = "";
    String b = "";
    String c = "";
    for(int i = 0; i < boa.length; i++){
      for(int j = 0; j < boa.length; j++){
        if(!boa[i][j].nw) {a += "\\";} else {a += " ";}
        if(!boa[i][j].n) { a += "|";} else {a += " ";}
        if(!boa[i][j].ne) { a += "/"; } else { a+= " ";}
        if(!boa[i][j].w) { b += "-" ;} else { b += " ";}
        if(i == row && j == col) { b += "f"; } else {b += "o";}
        if(!boa[i][j].e) {b += "-" ;} else { b += " ";}
        if(!boa[i][j].sw ) {c += "/";} else { c += " ";}
        if(!boa[i][j].s ) {c += "|" ;} else { c += " ";}
        if(!boa[i][j].se ) {c += "\\" ;} else { c+= " ";}
      }
      System.out.print(a + "\n" + b + "\n" + c + "\n");
      a = ""; b = ""; c = "";
    }
  }

  private int minimax(Node[][] b, int lplayer, int depth, int prow, int pcol, int origDepth) {
    int minScore = Integer.MAX_VALUE;
    int bestAction = -999;

    if (depth == 0) {
      // TODO: make better.
      if (distToGoal(row, col, lplayer) < distToGoal(prow, pcol, lplayer)) {
        return distToGoal(prow, pcol, lplayer);
      } else {
        return distToGoal(row, col, lplayer) - distToGoal(prow, pcol, lplayer);
      }
    }

    for (int i = 0; i < actions.size(); i++) {
      String action = actions.get(i);
      if (b[prow][pcol].isValid(action)) {

        // Deep copy.
        Node[][] local = new Node[15][15];
        for (int j = 0; j < b.length; j++) {
          for (int k = 0; k < b.length; k++) {
            local[j][k] = new Node(b[j][k]);
          }
        }

        Coords newCoords = updateBoard(local, action, prow, pcol, false);

        // A goal has been made!!
        if (newCoords.col == -999 && newCoords.row == -999) {
          if (depth == origDepth) {
            return i;
          } else {
            return Integer.MIN_VALUE;
          }
        }

        int lrow = newCoords.row;
        int lcol = newCoords.col;

        int opponentsScore = minimax(local, -lplayer, depth - 1, lrow, lcol, origDepth);

        if (opponentsScore < minScore) {
          bestAction = i;
          minScore = opponentsScore;
        }
      }
    }

    if (depth < origDepth) {
      return minScore;
    } else {
      return bestAction;
    }
  }

  private void play_game() throws IOException {

    Socket pingSocket = null;
    PrintWriter out = null;
    BufferedReader in = null;

    pingSocket = new Socket(this.host, this.port);
    out = new PrintWriter(pingSocket.getOutputStream(), true);
    in = new BufferedReader(new InputStreamReader(pingSocket.getInputStream()));
    String server_response = "";

    while (true) {

      server_response = in.readLine();

      System.out.println("Server said:" + server_response);

      if (server_response.equals("What's your name?")) {
        out.println(name + "\r");
      } else if (server_response.startsWith("Welcome, American")) {
          playerNum = Character.getNumericValue(server_response.charAt(server_response.length()-2));

          bestMove = (playerNum == 0) ? "north" : "south";

          if (player == 0) {
            player = 1;
            goalRow = 0;
          } else {
            player = -1;
            goalRow = 14;
          }

          initBoard();

      } else if (server_response.contains("did go")) {
        updateBoard(null, server_response, -1, -1, true);
        printBoard(board);
      } else {
        if (server_response.startsWith(name + " is active player") || server_response.startsWith("invalid move")) {

          int depth = 2;
          String msg = actions.get(minimax(board, player, depth, row, col, depth));
          System.out.println(msg);
          out.println(msg+"\r");
        } else if (server_response.startsWith("Game is on")) {
          System.out.println("Game ON");
        } else if (server_response.contains("won a goal was made") || server_response.contains("checkmate")) {
          System.out.println("Game is done");
          break;
        }
      }
    }
    out.close();
    in.close();
    pingSocket.close();
  }
}
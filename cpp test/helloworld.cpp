#include <typeinfo> 
#include <iostream>
#include <vector>
#include <unordered_map>
#include <cmath>
#include <algorithm>
#include <ctime>

class Connect4Node
{
private:
    static constexpr int ROWS = 6;
    static constexpr int COLS = 7;
    static constexpr int SHIFT_VALUES[ROWS][COLS] = {0};

    int board;
    int player;
    bool is_terminal;
    int last_move;
    std::vector<int> history;
    std::unordered_map<int, int> reward;
    std::unordered_map<int, int> total_reward;
    mutable std::vector<Connect4Node> children;
    int winner;
    std::unordered_map<int, int> Q;
    std::unordered_map<int, int> N;
    bool visited;
    std::unordered_map<int, int> win_count;
    int visit_count;
    int depth;
    std::vector<int> simulation_paths;
    bool simulated;
    std::unordered_map<int, int> uct_value;
    size_t hash;

public:
    // ... Constructors and other methods ...

    std::string detect_board_type(const std::vector<std::vector<int>> &board)
    {
        // In C++, we can just use typeid to get the type name
        return typeid(board).name();
    }

    // ... Rest of the class methods ...

    bool operator==(const Connect4Node &other) const
    {
        return board == other.board && history == other.history;
    }

    size_t get_hash() const
    {
        return hash;
    }

    // Translate the set_cell method
    void set_cell(int row, int col, int value)
    {
        int mask = 0b11 << (2 * (row * COLS + col));
        this->board = (this->board & ~mask) | (value << (2 * (row * COLS + col)));
    }

    // Translate the drop_piece method
    void drop_piece(int col, int piece)
    {
        int row = get_next_open_row(col);
        set_cell(row, col, piece);
    }

    // Translate the get_next_open_row method
    int get_next_open_row(int col) const
    {
        for (int r = 0; r < ROWS; ++r)
        {
            if (get_cell(r, col) == 0)
            {
                return r;
            }
        }
        return -1; // Invalid, all rows are filled for this column
    }

    // Translate the create_children method
    void create_children() const
    {
        std::vector<Connect4Node> children;
        for (int col = 0; col < COLS; ++col)
        {
            if (get_cell(ROWS - 1, col) == 0)
            {
                int new_board = this->board;
                for (int row = 0; row < ROWS; ++row)
                {
                    if (get_cell(row, col) == 0)
                    {
                        int opponent = 3 - this->player;
                        Connect4Node new_node(new_board, opponent, col); // Assume a constructor with these parameters exists
                        new_node.set_cell(row, col, opponent);
                        bool is_terminal, player_win;
                        std::tie(is_terminal, player_win) = new_node.check_terminal(); // Assuming check_terminal returns a tuple
                        new_node.winner = player_win ? opponent : 0;
                        new_node.is_terminal = is_terminal;
                        children.push_back(new_node);
                        break;
                    }
                }
            }
        }

        this->children = children;
    }

    // Translate the check_terminal method
    std::pair<bool, bool> check_terminal() const
    {
        std::vector<std::pair<int, int>> directions = {
            {0, 1}, {1, 0}, {1, 1}, {1, -1}};

        for (int row = 0; row < ROWS; ++row)
        {
            for (int col = 0; col < COLS; ++col)
            {
                int current_cell = get_cell(row, col);
                if (current_cell == 0)
                {
                    continue;
                }

                for (const auto &dir : directions)
                {
                    int dr = dir.first, dc = dir.second;
                    if (row + 3 * dr < ROWS && col + 3 * dc >= 0 && col + 3 * dc < COLS)
                    {
                        int count = 0;
                        for (int i = 0; i < 4; ++i)
                        {
                            if (get_cell(row + i * dr, col + i * dc) == current_cell)
                            {
                                count++;
                            }
                            else
                            {
                                break;
                            }
                        }
                        if (count == 4)
                        {
                            return {true, true};
                        }
                    }
                }
            }
        }

        for (int i = 0; i < ROWS * COLS; ++i)
        {
            int cell_value = (this->board >> (2 * i)) & 0b11;
            if (cell_value == 0)
            {
                return {false, false};
            }
        }

        return {true, false};
    }

    // Translate the int_to_board method
    std::vector<std::vector<int>> int_to_board() const
    {
        std::vector<std::vector<int>> board(ROWS, std::vector<int>(COLS, 0));
        int mask = 0b11;
        for (int row = 0; row < ROWS; ++row)
        {
            for (int col = 0; col < COLS; ++col)
            {
                int pos = 2 * (row * COLS + col);
                board[row][col] = (this->board >> pos) & mask;
            }
        }
        return board;
    }

    // Translate the board_to_int method
    int board_to_int(const std::vector<std::vector<int>> &board)
    {
        int board_int = 0;
        for (int row = 0; row < ROWS; ++row)
        {
            for (int col = 0; col < COLS; ++col)
            {
                int value = board[row][col];
                int shift_value = 2 * (row * COLS + col);
                board_int |= (value << shift_value);
            }
        }
        return board_int;
    }

    // Translate the get_cell method, replacing lru_cache with our own caching mechanism
    // This is a simplified caching mechanism for demonstration purposes
    mutable std::unordered_map<int, int> get_cell_cache;
    int get_cell(int row, int col) const
    {
        int key = row * 10 + col; // Assuming col will always be a single digit
        if (get_cell_cache.find(key) != get_cell_cache.end())
        {
            return get_cell_cache[key];
        }

        int shift_value = 2 * (row * COLS + col);
        int mask = 0b11 << shift_value;
        int value = (this->board & mask) >> shift_value;

        get_cell_cache[key] = value; // Cache the result
        return value;
    }

    // Translate the is_board_full method
    bool is_board_full() const
    {
        int mask = 0b11;
        for (int i = 0; i < ROWS * COLS; ++i)
        {
            int cell_value = (this->board >> (2 * i)) & mask;
            if (cell_value == 0)
            {
                return false;
            }
        }
        return true;
    }

    // Translate the is_terminal method
    bool is_terminal2() const
    {
        return this->is_terminal;
    }

    // Translate the get_valid_moves method
    std::vector<int> get_valid_moves() const
    {
        std::vector<int> valid_moves;
        for (const auto &child : this->children)
        {
            int col = child.last_move;
            if (get_cell(ROWS - 1, col) == 0)
            {
                valid_moves.push_back(col);
            }
        }
        return valid_moves;
    }

    // Translate the is_valid_location method
    bool is_valid_location(int col) const
    {
        return get_cell(ROWS - 1, col) == 0;
    }

    // Translate the find_random_child method
    Connect4Node find_random_child() const
    {
        if (is_terminal)
        {
            // Return a default node (you'll need to define a default constructor)
            return Connect4Node();
        }

        if (this->children.empty())
        {
            // Assuming create_children has been adjusted to modify the current object's children
            this->create_children();
            int random_index = std::rand() % this->children.size();
            return this->children[random_index];
        }
        else
        {
            auto available_moves = get_valid_moves();
            return _uct_select(available_moves);
        }
    }

    // Translate the _uct_select method
    Connect4Node _uct_select(const std::vector<int> &nodeList) const
    {
        double total_simulations = static_cast<double>(this->N.at(1) + this->N.at(2));
        total_simulations = (total_simulations == 0) ? 1 : total_simulations;
        double log_N = std::log(total_simulations);

        auto uct = [](const Connect4Node& n, double total_simulations)
        {
            double N = static_cast<double>(n.N.at(n.player) + 1);
            double Q = static_cast<double>(n.Q.at(n.player));
            double C = 2.0;

            double exploitation_value = n.win_count.at(n.player) / N;

            double exploration_value = (total_simulations > 0) ? C * std::sqrt(log_N / N) : 0;

            return exploitation_value + exploration_value;
        };

        // Find the node with the highest UCT value
        double max_val = -std::numeric_limits<double>::infinity();
        Connect4Node *best_node;

        for (const auto &node : nodeList)
        {
            double current_val = uct(node, total_simulations);
            if (current_val > max_val)
            {
                max_val = current_val;
                best_node = node;
            }
        }

        return best_node;
    }

  // Translate the evaluate_board method
    int evaluate_board() const {
        int score = 0;

        std::unordered_map<int, int> PATTERN_SCORES = {
            {4, 1000},  // Four in a line
            {3, 100},   // Three in a line
            {2, 10}     // Two in a line
        };

        for (int pattern_len = 4; pattern_len >= 2; --pattern_len) {
            int patterns_count = count_potential_patterns(this->player, pattern_len);
            score += PATTERN_SCORES[pattern_len] * patterns_count;
        }

        return score;
    }

    // Translate the count_potential_patterns method
    int count_potential_patterns(int player, int length) const {
        int count = 0;
        std::vector<std::pair<int, int>> directions = {
            {1, 0}, {0, 1}, {1, 1}, {1, -1}
        };

        int empty_spaces_needed = 4 - length;

        for (const auto& dir : directions) {
            int dx = dir.first, dy = dir.second;
            for (int i = 0; i < ROWS; ++i) {
                for (int j = 0; j < COLS; ++j) {
                    if (i + 3 * dx >= ROWS || j + 3 * dy < 0 || j + 3 * dy >= COLS) {
                        continue;
                    }

                    std::vector<int> pattern;
                    for (int k = 0; k < 4; ++k) {
                        pattern.push_back(get_cell(i + k * dx, j + k * dy));
                    }

                    if (std::count(pattern.begin(), pattern.end(), player) == length &&
                        std::count(pattern.begin(), pattern.end(), 0) == empty_spaces_needed) {
                        count++;
                    }
                }
            }
        }

        return count;
    }

    // Translate the update_win_count method
    void update_win_count(int winner) {
        if (win_count.find(winner) != win_count.end()) {
            win_count[winner]++;
        }
    }

 // Translate the update_node method
    void update_node(int board, int last_move, int new_player, int winner = 0) {
        if (board != 0) {
            this->board = board;
            // std::string type = detect_board_type(board);
            // if (type == "std::vector<std::vector<int>>") {
            //     this->board = board_to_int(board);
            // } else if (type == "int") {
            //     this->board = board;
            // }
        }
        this->player = new_player;
        this->last_move = last_move;
        this->history.push_back(last_move);
        this->winner = winner;
    }

    // Translate the create_from_existing method
    Connect4Node create_from_existing(const Connect4Node& existing_node) {
        Connect4Node new_node(existing_node.board, existing_node.player, existing_node.is_terminal, existing_node.last_move, existing_node.history, existing_node.winner);
        // Assuming a constructor with these parameters exists
        return new_node;
    }

    // Translate the detect_board_type method
    std::string detect_board_type(const auto& board) const {
        return typeid(board).name(); // Uses RTTI (RunTime Type Information) to determine the type of board
    }

    // Translate the __eq__ method to an operator overload
    bool equals(const Connect4Node& other) const {
        return this->board == other.board && this->history == other.history;
    }

    // Translate the __hash__ method
    // size_t hash() const {
    //     return std::hash<int>()(this->board) ^ std::hash<std::vector<int>>()(this->history);
    // }        
};

// You'd also need to define other utility functions and convert other methods ...

int main()
{
    // This would be where you test or utilize the class
    return 0;
}

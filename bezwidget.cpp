#include <iostream>
#include <cstdint>
#include <concepts>
#include <random>
#include <vector>
#include <fstream>
#include <stdexcept>
#include <string>
#include <array>
#include <cmath>
#include <type_traits>
#include <cstring>
#include <format>
#include <algorithm>


#define MAX_ROWS_COLUMNS 2000
#define MAX_FACTORIAL 15
#define MAX_IGS_HEADER_LENGTH 1024

template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template <Numeric T>
struct distribution_selector;

template <std::integral T>
struct distribution_selector<T> {
    using type = std::uniform_int_distribution<T>;
};

template <std::floating_point T>
struct distribution_selector<T> {
    using type = std::uniform_real_distribution<T>;
};

template <Numeric T>
using Distribution = typename distribution_selector<T>::type;

template<Numeric T>
struct Point2{
	T x;
	T y;

  friend std::istream& operator>>(std::istream& input, Point2& p) {
        return input >> p.x >> p.y;
    }

  friend std::ostream& operator<<(std::ostream& os, const Point2& p) {
        return os << "(" << p.x << ", " << p.y <<")\t";
    }

    Point2& operator+=(const Point2& B) {
        x += B.x; y += B.y;
        return *this;
    }

    Point2& operator-=(const Point2& B) {
        x -= B.x; y -= B.y;
        return *this;
    }

    Point2& operator*=(T B) {
        x *= B; y *= B;
        return *this;
    }

    Point2& operator/=(T B) {
        x /= B; y /= B;
        return *this;
    }

    [[nodiscard]] Point2 operator+(const Point2& B) const { return Point2(*this) += B; }
    [[nodiscard]] Point2 operator-(const Point2& B) const { return Point2(*this) -= B; }
    [[nodiscard]] Point2 operator*(T B) const { return Point2(*this) *= B; }
    [[nodiscard]] Point2 operator/(T B) const { return Point2(*this) /= B; }
    [[nodiscard]] friend Point2 operator*(T scalar, const Point2& point) {
        return point * scalar; 
    }
};

template<Numeric T>
struct Point4{
	T x;
	T y;
	T z;
	T w;
  friend std::istream& operator>>(std::istream& input, Point4& p) {
        return input >> p.x >> p.y >> p.z >> p.w;
    }
  friend std::ostream& operator<<(std::ostream& os, const Point4& p) {
        return os << "(" << p.x << ", " << p.y << ", " << p.z << ", " << p.w << ")\t";
    }

    Point4& operator+=(const Point4& B) {
        x += B.x; y += B.y; z += B.z; w += B.w;
        return *this;
    }

    Point4& operator-=(const Point4& B) {
        x -= B.x; y -= B.y; z -= B.z; w += B.w;
        return *this;
    }

    Point4& operator*=(T B) {
        x *= B; y *= B; z *= B; w *= B;
        return *this;
    }

    Point4& operator/=(T B) {
        x /= B; y /= B; z /= B; w /=B;
        return *this;
    }

    [[nodiscard]] Point4 operator+(const Point4& B) const { return Point4(*this) += B; }
    [[nodiscard]] Point4 operator-(const Point4& B) const { return Point4(*this) -= B; }
    [[nodiscard]] Point4 operator*(T B) const { return Point4(*this) *= B; }
    [[nodiscard]] Point4 operator/(T B) const { return Point4(*this) /= B; }
    [[nodiscard]] friend Point4 operator*(T scalar, const Point4& point) {
        return point * scalar; 
    }
  
};


template<Numeric T>
struct Point3{
	T x;
	T y;
	T z;
  friend std::istream& operator>>(std::istream& input, Point3& p) {
        return input >> p.x >> p.y >> p.z;
    }
  friend std::ostream& operator<<(std::ostream& os, const Point3& p) {
        return os << "(" << p.x << ", " << p.y << ", " << p.z << ")\t";
    }

    Point3& operator+=(const Point3& B) {
        x += B.x; y += B.y; z += B.z;
        return *this;
    }

    Point3& operator+=(const Point4<T>& B) {
        x += B.x; y += B.y; z += B.z;
        return *this;
    }
	///
    Point3& operator-=(const Point3& B) {
        x -= B.x; y -= B.y; z -= B.z;
        return *this;
    }

    Point3& operator-=(const Point4<T>& B) {
        x -= B.x; y -= B.y; z -= B.z;
        return *this;
    }

    Point3& operator*=(T B) {
        x *= B; y *= B; z *= B;
        return *this;
    }

    Point3& operator/=(T B) {
        x /= B; y /= B; z /= B;
        return *this;
    }

    [[nodiscard]] Point3 operator+(const Point3& B) const { return Point3(*this) += B; }
    [[nodiscard]] Point3 operator+(const Point4<T>& B) const { return Point3(*this) += B; }
    [[nodiscard]] Point3 operator-(const Point3& B) const { return Point3(*this) -= B; }
    [[nodiscard]] Point3 operator-(const Point4<T>& B) const { return Point3(*this) -= B; }
    [[nodiscard]] Point3 operator*(T B) const { return Point3(*this) *= B; }
    [[nodiscard]] Point3 operator/(T B) const { return Point3(*this) /= B; }
    [[nodiscard]] friend Point3 operator*(T scalar, const Point3& point) {
        return point * scalar; 
    }
};


template<typename T>
concept Point = std::is_aggregate_v<T> && (
    sizeof(T) <= (4 * alignof(T)) && 
    sizeof(T) >= (2 * alignof(T))
);


struct any_type {
    template<class U>
    constexpr operator U() const noexcept;

};

template<typename T>
concept IsPoint2 =
    Point<T> &&
    requires { T{any_type{}, any_type{}}; } &&
    (!requires { T{any_type{}, any_type{}, any_type{}}; });

template<typename T>
concept IsPoint3 =
    Point<T> &&
    requires { T{any_type{}, any_type{}, any_type{}}; } &&
    (!requires { T{any_type{}, any_type{}, any_type{}, any_type{}}; });

template<typename T>
concept IsPoint4 =
    Point<T> &&
    requires { T{any_type{}, any_type{}, any_type{}, any_type{}}; } &&
    (!requires { T{any_type{}, any_type{}, any_type{}, any_type{}, any_type{}}; });



constexpr unsigned long long factorial(int n) {
    return (n <= 1) ? 1 : n * factorial(n - 1);
}

template <std::size_t... Is>
constexpr std::array<unsigned long long, sizeof...(Is)> make_factorials(std::index_sequence<Is...>) {
    return { factorial(Is)... };
}

template <std::size_t N = MAX_FACTORIAL>
constexpr auto Factorials = make_factorials(std::make_index_sequence<N>{});


int get_random_range(int a, int b, std::mt19937& generator) {
    std::uniform_int_distribution<int> distrib(a, b);
    return distrib(generator);
}

template<Numeric T,  typename Dist>
T get_random_number(std::mt19937 &generator, Dist& dist){
	return dist(generator);
};

template<Numeric T, Point PointType>
class MatrixOfPoints{
	public:
	size_t rows, columns;
	
	std::vector<PointType> data;

	MatrixOfPoints(size_t r, size_t c) : rows(r), columns(c), data(r * c){};
	PointType& operator()(size_t r, size_t c){ return data[r * columns + c];}; 

	void FillRandomValues(PointType Dimensions, PointType Delta, PointType Center,std::mt19937& generator){
		
		Distribution<T> dist_x(-Delta.x, Delta.x);
		Distribution<T> dist_y(-Delta.y, Delta.y);
		Distribution<T> dist_z(-Delta.z, Delta.z);
		if constexpr (IsPoint2<PointType>){
			for (size_t i = 0; i < rows; i++){
				for (size_t j = 0; j < columns; j++){
					this->operator()(i, j) = {Center.x +  ( (((T) 2 * j) / ((T) (columns - 1)) ) - (T) 1) * 0.5 * Dimensions.x + get_random_number<T, Distribution<T>>(generator, dist_x), Center.y + get_random_number<T, Distribution<T>>(generator, dist_y)};
				}
			}
		};
		if constexpr (IsPoint3<PointType>){
			for (size_t i = 0; i < rows; i++){
				for (size_t j = 0; j < columns; j++){
					this->operator()(i, j) = {Center.x +  ( (((T) 2 * j) / ((T) (columns - 1)) ) - (T) 1) * 0.5 * Dimensions.x + get_random_number<T, Distribution<T>>(generator, dist_x), Center.y + ( (((T) 2 * i) / ((T) (rows - 1)) ) - (T) 1) * 0.5 * Dimensions.y + get_random_number<T, Distribution<T>>(generator, dist_y), Center.z  + get_random_number<T, Distribution<T>>(generator, dist_z) };


				}
			}
			return;
		};
		if constexpr (IsPoint4<PointType>){
			for (size_t i = 0; i < rows; i++){
				for (size_t j = 0; j < columns; j++){
					this->operator()(i, j) = {Center.x +  ( (((T) 2 * j) / ((T) (columns - 1)) ) - (T) 1) * 0.5 * Dimensions.x + get_random_number<T, Distribution<T>>(generator, dist_x), Center.y + ( (((T) 2 * i) / ((T) (rows - 1)) ) - (T) 1) * 0.5 * Dimensions.y + get_random_number<T, Distribution<T>>(generator, dist_y), Center.z  + get_random_number<T, Distribution<T>>(generator, dist_z) , (T) 1};
				}
			}
			return;
		};


	};


	friend std::ifstream& operator>>(std::ifstream &input, MatrixOfPoints &mat){
		if (mat.rows <= 0 || mat.columns <= 0 || mat.rows > MAX_ROWS_COLUMNS || mat.columns > MAX_ROWS_COLUMNS){
			throw std::out_of_range("Matrix object must be declared with rows and columns between 1 and" + std::to_string(MAX_ROWS_COLUMNS));
		};
		for (size_t i = 0; i < mat.rows; i++){
			for (size_t j = 0; j < mat.columns; j++){
				input >> mat(i,j);
			}
		}
		return input;
	};
	

	void printData(){
		for (size_t i = 0; i < this->rows; i++){
			for (size_t j = 0; j < this->columns; j++){
				std::cout << this->operator()(i,j);
			}
			std::cout << '\n';
		}
		
	}
};


template<Numeric T, Point PointType>
PointType DeCasteljau_u(MatrixOfPoints<T, PointType>& P, T u, T v){
		PointType PrevColumn[MAX_ROWS_COLUMNS - 1] = {0};
		PointType Q[MAX_ROWS_COLUMNS - 1] = {0};
		size_t k = P.columns - 1;
		size_t i = 0;
		size_t j = 0;
		for (j = 0; j < P.columns; j++){
			for (i = 0; i < P.rows - 1; i++){
				PrevColumn[i] = P(i,j) * (1 - u) + P(i + 1, j) * u;
			};
			for (k = 2; k < P.rows; k++){
				for (i = 0; i < P.rows - k; i++){
				PrevColumn[i] = PrevColumn[i] * (1 - u) + PrevColumn[i + 1] * u;
				};
			};
			Q[j] = PrevColumn[0];
		};
		for (k = 1; k < P.columns; k++){
			for (i = 0; i < P.columns - k; i++){
				Q[i] = Q[i] * (1 - v) + Q[i + 1] * v;
			};
		};
		return Q[0];
};


template<Numeric T, Point PointType>
Point3<T> CrossProduct(Point3<T> A, Point3<T> B){
	Point3<T> res = {0,0,0};
	res.x = A.y * B.z - A.z * B.y;
	res.y = A.z * B.x - A.x * B.z;
	res.z = A.x * B.y - A.y * B.x;
	return res;
};

template<Numeric T>
void Norm(Point3<T>& n){
	const T length = std::sqrt(n.x * n.x + n.y * n.y + n.z * n.z);
	n /= length;
};

template<Numeric T>
Point3<T> toPoint3(Point4<T> p){
	return {p.x / p.w, p.y / p.w, p.z / p.w};
};


template<Numeric T, Point PointType>
class BezierSurface{
	public:
	MatrixOfPoints<T, PointType> P;
	T DU;
	T DV;
	std::ofstream fp;
	T offset;
	BezierSurface(MatrixOfPoints<T, PointType> Points, T du, T dv) : P(Points), DU(du), DV(dv){};

	PointType S_curve(T u, T v){
		return DeCasteljau_u<T, PointType>(this->P, u,v);

	};

	Point3<T> NormalBruteForce(T u, T v) {

    	const size_t rows = this->P.rows;
    	const size_t columns = this->P.columns;

    	const size_t n = rows - 1;     
    	const size_t m = columns - 1;  


    	Point3<T> Su = {0, 0, 0};
    	Point3<T> Sv = {0, 0, 0};
		
    	Point3<T> normal = {0, 0, 0};

    	auto binomial = [](size_t degree, size_t k) -> T {
    	    return static_cast<T>(factorial(degree)) /
    	           (static_cast<T>(factorial(k)) *
    	            static_cast<T>(factorial(degree - k)));
    	};
    	auto Bernstein = [&](size_t degree, size_t k, T t) -> T {
    	    return binomial(degree, k) *
    	           std::pow(t, static_cast<int>(k)) *
    	           std::pow(static_cast<T>(1) - t, static_cast<int>(degree - k));
    	};
    	auto BernsteinDerivative = [&](size_t degree, size_t k, T t) -> T {
    	    if (degree == 0) {
    	        return static_cast<T>(0);
    	    }
    	    T result = static_cast<T>(0);

    	    const T c = binomial(degree, k);

    	    if (k > 0) {
    	        result += c *
    	                  static_cast<T>(k) *
    	                  std::pow(t, static_cast<int>(k - 1)) *
    	                  std::pow(static_cast<T>(1) - t,
    	                           static_cast<int>(degree - k));
    	    }

    	    if (k < degree) {
    	        result -= c *
    	                  static_cast<T>(degree - k) *
    	                  std::pow(t, static_cast<int>(k)) *
    	                  std::pow(static_cast<T>(1) - t,
    	                           static_cast<int>(degree - k - 1));
    	    }

    	    return result;
    	};


   	if constexpr (IsPoint4<PointType>) {
		Point3<T> Nu = 0;
		Point3<T> Nprimeu = 0;
		T Du = 0;
		T Dprimeu = 0;

		Point3<T> Nv = 0;
		Point3<T> Nprimev = 0;
		T Dv = 0;
		T Dprimev = 0;

    	for (size_t i = 0; i < rows; i++) {
    	    for (size_t j = 0; j < columns; j++) {
    	        const T Bu  = Bernstein(n, i, u);
    	        const T Bv  = Bernstein(m, j, v);
    	        const T dBu = BernsteinDerivative(n, i, u);
    	        const T dBv = BernsteinDerivative(m, j, v);
				
				Du = Du + Bu * Bv * this->P(i,j).w;
				Nprimeu = Nprimeu + dBu * Bv * this->P(i,j);
				Nu = Nu + Bu * Bv * this->P(i,j);
				Dprimeu = Dprimeu + dBu * Bv * this->P(i,j).w;

				Dv = Dv + Bu * Bv * this->P(i,j).w;
				Nprimev = Nprimev + Bu * dBv * this->P(i,j);
				Nv = Nv + Bu * Bv * this->P(i,j);
				Dprimev = Dprimev + Bu * dBv * this->P(i,j).w;
    	    }
    	}
			Su = ( Du * Nprimeu - Nu * Dprimeu )/ (Dprimeu * Dprimeu);
			Sv = ( Dv * Nprimev - Nv * Dprimev )/ (Dprimev * Dprimev);

   	 } else {

    	for (size_t i = 0; i < rows; i++) {
    	    for (size_t j = 0; j < columns; j++) {
    	        const T Bu  = Bernstein(n, i, u);
    	        const T Bv  = Bernstein(m, j, v);
    	        const T dBu = BernsteinDerivative(n, i, u);
    	        const T dBv = BernsteinDerivative(m, j, v);

    	        Su = Su + (dBu * Bv) * this->P(i, j);
    	        Sv = Sv + (Bu * dBv) * this->P(i, j);
    	    }
    	}
	  };

    	normal = CrossProduct(Su, Sv);
    	Norm(normal);

    	return normal;
	}
	
	void S(T u , T v){
		Point3<T> normal = NormalBruteForce(u , v);
		const PointType Point = S_curve(u , v);
		Point3<T> ptemp = {0,0,0};
		if constexpr (IsPoint4<PointType>){
			const Point3<T> ptemp = toPoint3(Point);


		};
		Point = S_curve(u , v) + offset * normal;
		
		T theta = std::acos(normal.z);
		T phi = std::atan(normal.x / normal.y);

		fp << "X" << Point.x << "\tY" << Point.y << "\tZ" << Point.z << "\tA" << theta << "\tB" << phi << "\n"; 
	};



	void ZigZag(){
		T u = 0;
		T v = 0;
		T du = this->DU;
		T dv = this->DV;
		while (v < 1){
			while (u < 1){
				S(u,v);
				u += du;
			};
			v += dv;
			while (u > 0){
				S(u, v);
				u -= du;
			};
			v += dv;
		};
	};
	void Spiral(){
		T u = 0;
		T v = 0;
		T du = this->DU;
		T dv = this->DV;
		T vmax = 1;
		T umax = 1;
		T vmin = 0;
		T umin = 0;
		while (vmax > vmin && umax > umin){
			while (v < vmax){
				S(u , v);
				v += dv;
			};
			while (u < umax){
				S(u , v);
				u += du;
			};
			while (v > vmin){
				S(u , v);
				v -= dv;
			};
			vmin += dv;
			umin += du;
			while (u > umin){
				S(u , v);
				u -= dv;
			};
			umax -= du;
			vmax -= dv;
		};

	 };

};

template<Numeric T>
struct igsSurface{
	uint32_t IGES_type;
	uint32_t Pstart;
	uint32_t External_schema;
	uint32_t Default_wireframe;
	uint32_t Layer;
	size_t TransformationMatrixPtr;
    static constexpr const char* label_assoc = "00000000";
	
	uint32_t line_weight_number;
	uint32_t color_number;
	uint32_t FormNumber;
	char surfaceName[8];
	MatrixOfPoints<T, Point4<T>> points;
	
};


template<Numeric T>
struct igsData{
	public:
	std::string FullHeader;
	std::string TITLE;
	std::vector<igsSurface<T>> Surfaces;
	FILE *igsFILE;

	inline void StringAdd(const char *str){
	std::format_to(std::back_inserter(this->FullHeader), "{}H{},", std::strlen(str), str);
	};

	igsData(const char* Title,	const char* Name,	const char* SourceName,	const char* FileName,	const char* precisiondata,	const char* scale, const char* date,	const char* minimum_resolution,	const char* maximum_coordinate,	const char* author,	const char* organization,	const char* IGES_version, std::vector<igsSurface<T>> surfaces){

	FullHeader.reserve(MAX_IGS_HEADER_LENGTH);
	TITLE = Title;
	FullHeader = "1H,,1H;,";
	StringAdd(Name);
	StringAdd(SourceName);
	StringAdd(FileName);
	FullHeader += "4HGIES,";
	FullHeader += precisiondata;
	FullHeader += scale;
	FullHeader += ",2,2HMM,1,1.,";
	StringAdd(date);
	FullHeader += minimum_resolution;
	FullHeader += ",";
	FullHeader += maximum_coordinate;
	FullHeader += ",";
	StringAdd(author);
	StringAdd(organization);
	FullHeader += IGES_version;
	FullHeader += ",0;";

	igsFILE = fopen(FileName, "w");
	fprintf(igsFILE, "%-72sS%7d\n", TITLE, 1);
	size_t i = 0;
	int line_idx = 1;
	const char* raw_data = FullHeader.data();
	for (i = 0; i < FullHeader.size(); i += 73){
		int chunk_size = static_cast<int>(std::min( (size_t) 73, FullHeader.size() - i));
        fprintf(igsFILE, "%.*s", chunk_size, raw_data + i);
		fprintf(igsFILE, "G%7d\n", line_idx++);
	};
/* 
	uint32_t IGES_type;
	uint32_t Pstart;
	uint32_t External_schema;
	uint32_t Default_wireframe;
	uint32_t Layer;
	size_t TransformationMatrixPtr;
    static constexpr const char* label_assoc = "00000000";
	
	uint32_t line_weight_number;
	uint32_t color_number;
	uint32_t FormNumber;
	char surfaceName[8];
	MatrixOfPoints<T, Point4<T>> points;
 *
 *
 *
 */

	for (i = 0; i < Surfaces.size(); i++){

		fprintf(igsFILE, "%8u", (unsigned int) Surfaces[i].IGES_type);

	};



	};




};



template<Numeric T, Point PointType>
class BezierIOstream {
	public:
	BezierSurface<T, PointType> bezierSurface;
	T DU;
	T DV;
	enum class CAD_File_type {
		igs,
		acs,
		pointcloud,
		gcode,
	};
	std::ofstream fp;
	CAD_File_type CurrentType;
	T feedRate;
	T offset;
	BezierIOstream(BezierSurface<T, PointType> bs, T du, T dv, const char* name, BezierIOstream<T, PointType>::CAD_File_type tp1) : bezierSurface(bs), DU(du), DV(dv){ 
	


	}

	BezierIOstream(BezierSurface<T, PointType> bs, T du, T dv, T FeedRate, T Offset, const char* name) : bezierSurface(bs), DU(du), DV(dv){ 
	//gcode

	}

	;

	void SetFile(const char* name, T feedingRate, T offset){
		fp.close();
		fp.open(name);
		this->feedRate = feedingRate;
		fp << "G01\tF" << feedingRate << "\t";
	};



};


int main(){
	FILE *fp = fopen("Tool_parameters.txt", "r");
	double R, gamma, Lf, Lh, Nflutes = 0;
	fscanf(fp, "%lf", &R);
	fscanf(fp, "%lf", &gamma);
	fscanf(fp, "%lf", &Lf);
	fscanf(fp, "%lf", &Lh);
	fscanf(fp, "%lf", &Nflutes);
	std::cout << "Selected tool Radius: " << R << "\n";
	std::cout << "Selected helix angle: " << gamma << "\n";
	std::cout << "Selected flute length: " << Lf << "\n";
	std::cout << "Selected handle length: " << Lh << "\n";
	std::cout << "Selected Number of flutes: " << Nflutes << "\n";
	std::random_device rd;
	std::mt19937 generator(rd());




	MatrixOfPoints<double, Point3<double>> MyMatrix(5, 4);
	std::ifstream MyFile("points.txt");

	MyFile >> MyMatrix;
	MyMatrix.printData();
	MatrixOfPoints<double, Point4<double>> ThisMatrix(6,5);
	ThisMatrix.FillRandomValues({30, 40, 3, 1}, {0.5, 0.5, 0.2, 1}, {0,0,0, 1}, generator);
	ThisMatrix.printData();



};
